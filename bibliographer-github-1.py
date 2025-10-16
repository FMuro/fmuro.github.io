#!./bin/python3
import json
from bibliographer.libbibliographer import get_bibtex_from_zbmath, get_json_from_zbmath, get_dict_from_arxiv, bibtex

bibtex_zbmath = get_bibtex_from_zbmath('muro.fernando')
dict_arxiv = get_dict_from_arxiv('0000-0001-8457-9889')
json_zbmath = get_json_from_zbmath('muro.fernando')

def handle_exceptions(string):
    return string.replace(
        "title = {Minimal ${A}_{\\infty}$-algebras of endomorphisms: {The} case of $d{{\\mathbb}}{Z}$-cluster tilting objects},",
        "title = {Minimal ${A}_{\\infty}$-algebras of endomorphisms: {The} case of $d\\mathbb{Z}$-cluster tilting objects},"
    )

bibtex_zbmath = handle_exceptions(bibtex_zbmath)

with open('bibtex.bib', 'w') as outfile:
    outfile.write(bibtex(bibtex_zbmath, json_zbmath, dict_arxiv, 2020))

with open('dict_arxiv.json', 'w') as outfile:
    json.dump(dict_arxiv, outfile, indent=4)

with open('json_zbmath.json', 'w') as outfile:
    json.dump(json_zbmath, outfile, indent=4)
