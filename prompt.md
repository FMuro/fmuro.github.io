I want to define in bibliographer.py a function called complete_zbmath. 

The input will be a two loaded YAML, zbmath_data and openalex_data, like the contents of zbmath.yaml and openalex.yaml. 

openalex_results = openalex_data.get("results", [])
openalex_exact, openalex_lower = build_openalex_lookup(openalex_results)

For each item zbmath_data['result'], do:

    arxiv_ID = get_arxiv_identifier_from_zbmath_item(item)

    if arxiv_ID:
        item['arxiv'] = arxiv_ID

    doi, title = get_doi_from_zbmath_item(item, openalex_exact, openalex_lower)

    if doi:
        item['doi'] = doi
        item['bibtex'] = get_paper_bibtex_from_crossref(DOI)
    elif arxiv_ID:
        item['bibtex'] = get_paper_bibtex_from_arxiv(arxiv_ID)

    arxiv_json = get_paper_JSON_from_arXiv(arxiv_ID)

    if arxiv_json contains some (sub)key called summary:
        item['abstract'] = value of that subkey

If any of the following values: 

item['source']['pages']
item['source']['source']
item['title']['title']

is:

conflict_str = 'zbMATH Open Web Interface contents unavailable due to conflicting licenses.'

crossref_json = get_paper_JSON_from_crossref(doi)

if item['source']['pages'] is conflict_str then replace if with: crossref_json['page']

if item['title']['title'] is conflict_str then replace if with: crossref_json['title'][0]

if item['source']['source'] is conflict_str then replace if with: item['source']['series']['short-title'] item['source']['series']['volume'], No. item['source']['series']['issue'], item['source']['pages'] (item['source']['series']['years'])