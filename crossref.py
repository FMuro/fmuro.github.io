import json
import os
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