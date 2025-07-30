#!./bin/python3
from bibliographer.libbibliographer import merged_data_dict
import yaml
import json

f = open('bibtex.bib', 'r')
bibtex = f.read()
f.close()

f = open('csl_json.json', 'r')
csl_json = json.loads(f.read())
f.close()

f = open('json_zbmath.json', 'r')
json_zbmath = json.loads(f.read())
f.close()

f = open('dict_arxiv.json', 'r')
dict_arxiv = json.loads(f.read())
f.close()

data = merged_data_dict(bibtex, csl_json, json_zbmath, dict_arxiv)

with open('output.yml', 'w') as outfile:
    yaml.dump(data, outfile, default_flow_style=False)
with open("output.json", "w") as outfile: 
    json.dump(data, outfile)