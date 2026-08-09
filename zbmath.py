import json
import urllib.error
import urllib.request
from urllib.parse import quote

import yaml

ZBMATH_API_URL = 'https://api.zbmath.org/v1/document/_search?search_string=ia%3A'


def _build_request(author_ID):
    url = f"{ZBMATH_API_URL}{quote(str(author_ID), safe='.-_')}"
    return urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
        },
    )


def _read_json_response(request):
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"zbMATH request failed with HTTP {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"zbMATH request failed: {exc.reason}") from exc

    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError("zbMATH returned invalid JSON") from exc


# This function retrieves the zbMATH Open publications by zbMATH author ID and returns them in JSON format
def get_JSON_from_zbmath(author_ID):
    request = _build_request(author_ID)
    return _read_json_response(request)


# This function retrieves the zbMATH Open publications by zbMATH author ID and returns them in YAML format
def get_YAML_from_zbmath(author_ID):
    data = get_JSON_from_zbmath(author_ID)
    return yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
