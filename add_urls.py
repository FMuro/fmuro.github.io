import yaml

with open("output.yaml", "r", encoding="utf-8") as f:
    zbmath = yaml.safe_load(f)

with open("data.yml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

coauthors = data.get("coauthors", {})

for item in zbmath.get("result", []):
    for author in item.get("authors", []):
        family = author.get("family")
        if family in coauthors:
            author["url"] = coauthors[family]

with open("output.yaml", "w", encoding="utf-8") as f:
    yaml.dump(
        zbmath,
        f,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )