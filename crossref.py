import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import yaml

CROSSREF_BASE_URL = "https://api.crossref.org/works"
DEFAULT_CROSSREF_AGENT = "bibliographer/1.0"


def get_paper_JSON_from_crossref(DOI):
    if not DOI:
        raise ValueError("DOI is required")

    mailto = os.environ.get("CROSSREF_MAILTO")
    agent = os.environ.get("CROSSREF_AGENT")
    encoded_DOI = urllib.parse.quote(DOI)
    url = f"{CROSSREF_BASE_URL}/{encoded_DOI}"
    if mailto:
        url = f"{url}?mailto={urllib.parse.quote(mailto)}"

    headers = {
        'Accept': 'application/json',
    }
    if agent:
        headers['User-Agent'] = agent
    elif mailto:
        headers['User-Agent'] = f"{DEFAULT_CROSSREF_AGENT} (mailto:{mailto})"
    else:
        headers['User-Agent'] = DEFAULT_CROSSREF_AGENT

    request = urllib.request.Request(
        url,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"CrossRef request failed with HTTP {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"CrossRef request failed: {exc.reason}") from exc

    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError("CrossRef returned invalid JSON") from exc


def get_paper_YAML_from_crossref(DOI):
    data = get_paper_JSON_from_crossref(DOI)
    return yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)


def _format_bibtex_string(bibtex: str) -> str:
    if not isinstance(bibtex, str):
        return bibtex

    lines = [line.lstrip() for line in bibtex.splitlines()]
    text = "\n".join(lines)
    text = re.sub(r",\s*(?=[A-Za-z0-9_]+\s*=)", ",\n", text)

    indented_lines = []
    for index, line in enumerate(text.splitlines()):
        if index == 0:
            indented_lines.append(line)
        else:
            indented_lines.append(f"    {line}")

    return "\n".join(indented_lines) + "\n"


def get_paper_bibtex_from_crossref(DOI):
    if not DOI:
        raise ValueError("DOI is required")

    mailto = os.environ.get("CROSSREF_MAILTO")
    agent = os.environ.get("CROSSREF_AGENT")
    encoded_DOI = urllib.parse.quote(DOI)
    url = f"{CROSSREF_BASE_URL}/{encoded_DOI}/transform/application/x-bibtex"
    if mailto:
        url = f"{url}?mailto={urllib.parse.quote(mailto)}"

    headers = {
        'Accept': 'application/x-bibtex',
    }
    if agent:
        headers['User-Agent'] = agent
    elif mailto:
        headers['User-Agent'] = f"{DEFAULT_CROSSREF_AGENT} (mailto:{mailto})"
    else:
        headers['User-Agent'] = DEFAULT_CROSSREF_AGENT

    request = urllib.request.Request(
        url,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request) as response:
            bibtex = response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"CrossRef request failed with HTTP {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"CrossRef request failed: {exc.reason}") from exc
    
    return _format_bibtex_string(bibtex)

