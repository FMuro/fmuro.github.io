#!/usr/bin/env python3
"""Download a fresh OpenVPN (UDP) configuration from the eduVPN portal of the
Universidad de Sevilla, logging in through the US SSO (adAS, SAML).

Usage:
    EDUVPN_USERNAME=... EDUVPN_PASSWORD=... python get_eduvpn_config.py out.ovpn

Optional environment variables:
    EDUVPN_PORTAL        default https://eduvpn.us.es/vpn-user-portal
    EDUVPN_PROFILE       profile id to use (default: first one offering OpenVPN/UDP)
    EDUVPN_DISPLAY_NAME  name shown in the portal (default: github-actions)
    EDUVPN_TOTP_SECRET   base32 seed of the US two-factor (TOTP) authenticator, or
                         the full otpauth://totp/... URI
    EDUVPN_DRY_RUN=1     only check that the SSO login form can be parsed

Previous configurations with the same display name are deleted first, so the
portal limit on active configurations is never reached.
"""

import base64
import hashlib
import hmac
import html
import os
import re
import struct
import sys
import time
from html.parser import HTMLParser
from urllib.parse import parse_qs, urljoin, urlparse

import requests

PORTAL = os.environ.get("EDUVPN_PORTAL", "https://eduvpn.us.es/vpn-user-portal").rstrip("/")
HOME = PORTAL + "/home"
DISPLAY_NAME = os.environ.get("EDUVPN_DISPLAY_NAME", "github-actions")
PROFILE = os.environ.get("EDUVPN_PROFILE", "").strip()
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")


def fail(msg):
    print(f"::error::{msg}", file=sys.stderr)
    sys.exit(1)


def totp(secret):
    """RFC 6238 code from a base32 seed or an otpauth:// URI."""
    digits, period, algo = 6, 30, "sha1"
    if secret.startswith("otpauth://"):
        q = {k: v[0] for k, v in parse_qs(urlparse(secret).query).items()}
        secret = q["secret"]
        digits = int(q.get("digits", 6))
        period = int(q.get("period", 30))
        algo = q.get("algorithm", "SHA1").lower()
    seed = re.sub(r"[\s-]", "", secret).upper()
    key = base64.b32decode(seed + "=" * (-len(seed) % 8))
    # do not use a code that is about to expire
    if period - time.time() % period < 3:
        time.sleep(4)
    counter = int(time.time() // period)
    mac = hmac.new(key, struct.pack(">Q", counter), getattr(hashlib, algo)).digest()
    offset = mac[-1] & 0x0F
    code = (struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF) % 10 ** digits
    return str(code).zfill(digits)


class FormParser(HTMLParser):
    """Collect every <form> with its inputs and <select> options."""

    def __init__(self):
        super().__init__()
        self.forms = []
        self._form = None
        self._select = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self._form = {"action": a.get("action") or "", "method": (a.get("method") or "get").lower(),
                          "id": a.get("id"), "inputs": {}, "selects": {}, "visible": []}
            self.forms.append(self._form)
        elif self._form is None:
            return
        elif tag == "input" and a.get("name"):
            itype = (a.get("type") or "text").lower()
            if itype in ("text", "password", "number", "tel"):
                self._form["visible"].append(a["name"])
            if itype in ("checkbox", "radio") and "checked" not in a:
                return
            self._form["inputs"][a["name"]] = a.get("value") or ""
        elif tag == "select" and a.get("name"):
            self._select = a["name"]
            self._form["selects"][self._select] = []
        elif tag == "option" and self._select is not None and a.get("value") is not None:
            self._form["selects"][self._select].append(a["value"])

    def handle_endtag(self, tag):
        if tag == "form":
            self._form = None
        elif tag == "select":
            self._select = None


def forms_of(page_html):
    p = FormParser()
    p.feed(page_html)
    return p.forms


def fetch_site(src_url, dst_url):
    s, d = urlparse(src_url), urlparse(dst_url)
    return "same-origin" if (s.scheme, s.netloc) == (d.scheme, d.netloc) else "cross-site"


def submit(session, page, form, extra=None):
    url = urljoin(page.url, html.unescape(form["action"])) if form["action"] else page.url
    data = dict(form["inputs"])
    data.update(extra or {})
    headers = {"Referer": page.url, "Sec-Fetch-Site": fetch_site(page.url, url),
               "Origin": "{0.scheme}://{0.netloc}".format(urlparse(page.url))}
    if form["method"] == "post":
        r = session.post(url, data=data, headers=headers, timeout=30)
    else:
        r = session.get(url, params=data, headers=headers, timeout=30)
    r.raise_for_status()
    return r


def login(session, username, password, dry_run=False):
    page = session.get(HOME, timeout=30)
    page.raise_for_status()
    if page.url.startswith(PORTAL):
        return page  # already logged in (should not happen with a fresh session)

    login_form = next((f for f in forms_of(page.text) if "adAS_username" in f["inputs"]), None)
    if login_form is None:
        fail(f"Could not find the SSO login form at {page.url}")
    if dry_run:
        print(f"SSO login form found at {urlparse(page.url).netloc}; dry run, stopping.")
        sys.exit(0)

    page = submit(session, page, login_form,
                  {"adAS_username": username, "adAS_password": password})

    # Follow the SAML round trip (second factor, SAMLResponse, consent, ...)
    # until we land back on the portal.
    otp_sent = False
    for _ in range(8):
        if page.url.startswith(PORTAL) and "add_config" in page.text:
            return page
        forms = forms_of(page.text)
        if any("adAS_username" in f["inputs"] for f in forms):
            fail("SSO login failed: check EDUVPN_USERNAME / EDUVPN_PASSWORD.")
        saml = next((f for f in forms if "SAMLResponse" in f["inputs"]), None)
        if saml:
            page = submit(session, page, saml)
            continue
        otp_form, otp_field = find_otp_form(forms)
        if otp_form:
            if otp_sent:
                fail("The SSO rejected the two-factor code: check EDUVPN_TOTP_SECRET "
                     "(and that the runner clock is right).")
            secret = os.environ.get("EDUVPN_TOTP_SECRET", "").strip()
            if not secret:
                fail("The SSO asks for a two-factor code but EDUVPN_TOTP_SECRET is not set.")
            print("Submitting two-factor code.")
            page = submit(session, page, otp_form, {otp_field: totp(secret)})
            otp_sent = True
            continue
        if len(forms) == 1:
            page = submit(session, page, forms[0])
            continue
        break

    if page.url.startswith(PORTAL):
        return session.get(HOME, timeout=30)
    debug_forms(page)
    fail(f"Login did not reach the eduVPN portal (stopped at {urlparse(page.url).netloc}"
         f"{urlparse(page.url).path}).")


def find_otp_form(forms):
    """Return (form, field) for a form asking for a single one-time code."""
    candidates = []
    for f in forms:
        fields = [n for n in f["visible"] if n not in ("adAS_username", "adAS_password")]
        if len(fields) != 1:
            continue  # e.g. the HOTP resync form asks for three codes
        named = re.search(r"otp|code|codigo|token|2f|factor|i2f", fields[0], re.I)
        candidates.append((0 if named else 1, f, fields[0]))
    if not candidates:
        return None, None
    _, form, field = min(candidates, key=lambda c: c[0])
    return form, field


def debug_forms(page):
    """Print the structure of the forms (names only, never values) to help debugging."""
    title = re.search(r"<title>(.*?)</title>", page.text, re.S)
    print(f"Page: {urlparse(page.url).netloc}{urlparse(page.url).path} "
          f"title={title.group(1).strip() if title else None!r}")
    for f in forms_of(page.text):
        print(f"  form id={f['id']!r} method={f['method']} "
              f"action={urlparse(html.unescape(f['action'])).path!r} "
              f"inputs={list(f['inputs'])} visible={f['visible']} selects={list(f['selects'])}")


def delete_old_configs(session, home):
    for row in re.findall(r"<tr>(.*?)</tr>", home.text, re.S):
        titles = [html.unescape(t) for t in re.findall(r'<span title="([^"]*)"', row)]
        conn = re.search(r'name="connectionId" value="([^"]+)"', row)
        action = 'value="delete_config"' in row
        if conn and action and DISPLAY_NAME in titles:
            session.post(HOME, data={"action": "delete_config",
                                     "connectionId": html.unescape(conn.group(1))},
                         headers={"Referer": HOME, "Origin": urlparse(HOME)._replace(path="").geturl(),
                                  "Sec-Fetch-Site": "same-origin"}, timeout=30).raise_for_status()
            print(f"Deleted previous configuration '{DISPLAY_NAME}'.")


def main():
    if len(sys.argv) != 2:
        fail("usage: get_eduvpn_config.py OUTPUT.ovpn")
    out = sys.argv[1]
    dry_run = os.environ.get("EDUVPN_DRY_RUN") == "1"
    username = os.environ.get("EDUVPN_USERNAME", "")
    password = os.environ.get("EDUVPN_PASSWORD", "")
    if not dry_run and not (username and password):
        fail("EDUVPN_USERNAME and EDUVPN_PASSWORD must be set.")

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept-Language": "es,en;q=0.8"})

    home = login(session, username, password, dry_run)
    delete_old_configs(session, home)
    home = session.get(HOME, timeout=30)

    form = next((f for f in forms_of(home.text) if f["inputs"].get("action") == "add_config"), None)
    if form is None:
        fail("No 'add_config' form on the portal (limit of active configurations reached?).")
    options = [o for o in form["selects"].get("profileId", []) if o.endswith("_openvpn+udp")]
    print("Available OpenVPN/UDP profiles:", ", ".join(o.split("_")[0] for o in options) or "none")
    if PROFILE:
        options = [o for o in options if o == f"{PROFILE}_openvpn+udp"]
    if not options:
        fail("No matching OpenVPN (UDP) profile available.")

    r = submit(session, home, form, {"profileId": options[0], "displayName": DISPLAY_NAME})
    config = r.text
    if "BEGIN" not in config or not re.search(r"^remote ", config, re.M):
        fail("The portal response does not look like an OpenVPN configuration.")
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(config)
    print(f"OpenVPN configuration for profile '{options[0].split('_')[0]}' written to {out}.")


if __name__ == "__main__":
    main()
