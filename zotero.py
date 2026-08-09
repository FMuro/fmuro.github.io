import json
import requests
import yaml


def get_JSON_from_zotero(Zotero_user_ID, Zotero_api_key, Zotero_collection_ID, limit=100):
    api_url = f"https://api.zotero.org/users/{Zotero_user_ID}/collections/{Zotero_collection_ID}/items?key={Zotero_api_key}"
    params = {
        "format": "json",
        "limit": limit,
    }
    response = requests.get(api_url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def get_YAML_from_zotero(Zotero_user_ID, Zotero_api_key, Zotero_collection_ID, limit=100):
    data = get_JSON_from_zotero(Zotero_user_ID, Zotero_api_key, Zotero_collection_ID, limit)
    return yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)