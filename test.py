import argparse
import json

ORCID = "0000-0001-8457-9889"
zbMATH = "muro.fernando"
OpenAlex = "A5015527081"
arXiv_ID = "muro_f_1"
arxiv_author_search_string = "muro+f"
CROSSREF_MAILTO = "fmuro@us.es"
Zotero_user_ID = "2837437"
Zotero_api_key = "g5elGNLIDbcjq0iMe4Ibsq8j"
Zotero_collection_ID = "G7G8AAAU"

from arxiv import *
from zbmath import *
from openalex import *
from DOI import *
from crossref import *
from zotero import *


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run bibliographer provider tests")
    parser.add_argument("-arxiv", action="store_true", help="run arXiv tests")
    parser.add_argument("-zbmath", action="store_true", help="run zbMATH tests")
    parser.add_argument("-openalex", action="store_true", help="run OpenAlex tests")
    parser.add_argument("-crossref", action="store_true", help="run CrossRef tests")
    parser.add_argument("-zotero", action="store_true", help="run Zotero tests")
    parser.add_argument("-bibtex", action="store_true", help="run BibTeX tests")
    parser.add_argument("-all", action="store_true", help="run all provider tests")
    return parser.parse_args(argv)


def get_selected_providers(args):
    if args.all:
        return {"arxiv", "zbmath", "openalex", "crossref", "zotero", "bibtex"}

    selected = set()
    if getattr(args, "arxiv", False):
        selected.add("arxiv")
    if getattr(args, "zbmath", False):
        selected.add("zbmath")
    if getattr(args, "openalex", False):
        selected.add("openalex")
    if getattr(args, "crossref", False):
        selected.add("crossref")
    if getattr(args, "zotero", False):
        selected.add("zotero")
    if getattr(args, "bibtex", False):
        selected.add("bibtex")

    if not selected:
        return {"arxiv", "zbmath", "openalex", "crossref", "zotero", "bibtex"}

    return selected


def run_arxiv_tests():
    print("\nTest arXiv functions:\n")

    try:
        JSON = get_JSON_from_arXiv(ORCID)
        print("JSON retrieval successful")
        with open("arxiv.json", "w", encoding="utf-8") as f:
            json.dump(JSON, f, ensure_ascii=False, indent=2)
        print("Saved JSON to arxiv.json\n")
    except Exception as e:
        print("JSON retrieval failed:", e, "\n")

    try:
        YAML = get_YAML_from_arXiv(ORCID)
        print("YAML retrieval successful")
        with open("arxiv.yaml", "w", encoding="utf-8") as f:
            f.write(YAML)
        print("Saved YAML to arxiv.yaml\n")
    except Exception as e:
        print("YAML retrieval failed:", e, "\n")

    try:
        RSS = get_search_output_from_string(arxiv_author_search_string)
        print("Search output retrieval successful")
        with open("arxiv.xml", "w", encoding="utf-8") as rf:
            rf.write(RSS)
        print("Saved RSS to arxiv.xml\n")
    except Exception as e:
        print("Search output retrieval failed:", e, "\n")


def run_zbmath_tests():
    print("Test zbMATH functions:\n")

    try:
        JSON = get_JSON_from_zbmath(zbMATH)
        print("JSON retrieval successful")
        with open("zbmath.json", "w", encoding="utf-8") as f:
            json.dump(JSON, f, ensure_ascii=False, indent=2)
        print("Saved JSON to zbmath.json\n")
    except Exception as e:
        print("JSON retrieval failed:", e, "\n")

    try:
        YAML = get_YAML_from_zbmath(zbMATH)
        print("YAML retrieval successful")
        with open("zbmath.yaml", "w", encoding="utf-8") as f:
            f.write(YAML)
        print("Saved YAML to zbmath.yaml\n")
    except Exception as e:
        print("YAML retrieval failed:", e, "\n")


def run_openalex_tests():
    print("Test OpenAlex functions:\n")

    try:
        JSON = get_JSON_from_openalex(ORCID)
        print("JSON retrieval successful")
        with open("openalex.json", "w", encoding="utf-8") as f:
            json.dump(JSON, f, ensure_ascii=False, indent=2)
        print("Saved JSON to openalex.json\n")
    except Exception as e:
        print("JSON retrieval failed:", e, "\n")

    try:
        YAML = get_YAML_from_openalex(ORCID)
        print("YAML retrieval successful")
        with open("openalex.yaml", "w", encoding="utf-8") as f:
            f.write(YAML)
        print("Saved YAML to openalex.yaml\n")
    except Exception as e:
        print("YAML retrieval failed:", e, "\n")


def run_crossref_tests():
    print("Test CrossRef functions:\n")

    DOI_list = get_doi_list_from_yaml_files("zbmath.yaml", "openalex.yaml")

    # Create or truncate the output files before running tests.
    with open("crossref.yaml", "w", encoding="utf-8"):
        pass

    for DOI in DOI_list:
        if 'arxiv' not in DOI.lower():
            try:
                YAML = get_paper_YAML_from_crossref(DOI)

                lines = YAML.split('\n')
                if len(lines) > 4:
                    lines = lines[4:]
                    if lines and lines[0]:
                        lines[0] = '-' + lines[0][1:]
                    YAML = '\n'.join(lines)

                with open("crossref.yaml", "a", encoding="utf-8") as f:
                    f.write(YAML)
                    f.write("\n")

            except Exception as e:
                print("YAML retrieval failed:", e, "\n")
                print(f"Failed YAML DOI: {DOI}\n")

    print("Saved YAML to crossref.yaml")


def run_bibtex_tests():
    print("Test BibTeX functions:\n")

    DOI_list = get_doi_list_from_yaml_files("zbmath.yaml", "openalex.yaml")

    # Create or truncate the output files before running tests.
    with open("bibtex.bib", "w", encoding="utf-8"):
        pass

    for DOI in DOI_list:
        try:
            if 'arxiv' in DOI.lower():
                bibtex = get_paper_bibtex_from_arxiv(DOI)
            else:
                bibtex = get_paper_bibtex_from_crossref(DOI)
            with open("bibtex.bib", "a", encoding="utf-8") as f:
                f.write(bibtex)
                if not bibtex.endswith("\n"):
                    f.write("\n")
        except Exception as e:
            print("BibTeX retrieval failed:", e, "\n")
            print(f"Failed BibTeX DOI: {DOI}\n")
    
    print("Saved BibTeX to crossref.bib\n")


def run_zotero_tests():
    print("Test Zotero functions:\n")

    try:
        JSON = get_JSON_from_zotero(Zotero_user_ID, Zotero_api_key, Zotero_collection_ID)
        print("JSON retrieval successful")
        with open("zotero.json", "w", encoding="utf-8") as f:
            json.dump(JSON, f, ensure_ascii=False, indent=2)
        print("Saved JSON to zotero.json\n")
    except Exception as e:
        print("JSON retrieval failed:", e, "\n")

    try:
        YAML = get_YAML_from_zotero(Zotero_user_ID, Zotero_api_key, Zotero_collection_ID)
        print("YAML retrieval successful")
        with open("zotero.yaml", "w", encoding="utf-8") as f:
            f.write(YAML)
        print("Saved YAML to zotero.yaml\n")
    except Exception as e:
        print("YAML retrieval failed:", e, "\n")


def main(argv=None):
    args = parse_args(argv)
    selected = get_selected_providers(args)

    if "arxiv" in selected:
        run_arxiv_tests()
    if "zbmath" in selected:
        run_zbmath_tests()
    if "openalex" in selected:
        run_openalex_tests()
    if "crossref" in selected:
        run_crossref_tests()
    if "zotero" in selected:
        run_zotero_tests()
    if "bibtex" in selected:
        run_bibtex_tests()
if __name__ == "__main__":
    main()