import urllib.request
import feedparser
import json
import yaml

atom = 'https://arxiv.org/a/'
BibTeX = 'https://arxiv.org/bibtex/'
RSS = "http://export.arxiv.org/api/query?search_query=au:"

# This function retrieves from arXiv the JSON feed of the publications of a given author ORCID
def get_JSON_from_arXiv(ORCID):
    return feedparser.parse(atom+ORCID+'.atom2')

# This function retrieves from arXiv the YAML feed of the publications of a given author ORCID
def get_YAML_from_arXiv(ORCID):
    data = get_JSON_from_arXiv(ORCID)
    return yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)

# This function retrieves from arXiv the RSS feed of the publications of a given author name
def get_search_output_from_string(author):
    return urllib.request.urlopen(RSS+author).read().decode('utf-8')