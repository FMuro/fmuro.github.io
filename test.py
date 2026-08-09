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
from crossref import *
from zotero import *


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run bibliographer provider tests")
    parser.add_argument("-arxiv", action="store_true", help="run arXiv tests")
    parser.add_argument("-zbmath", action="store_true", help="run zbMATH tests")
    parser.add_argument("-openalex", action="store_true", help="run OpenAlex tests")
    parser.add_argument("-crossref", action="store_true", help="run CrossRef tests")
    parser.add_argument("-zotero", action="store_true", help="run Zotero tests")
    parser.add_argument("-all", action="store_true", help="run all provider tests")
    return parser.parse_args(argv)


def get_selected_providers(args):
    if args.all:
        return {"arxiv", "zbmath", "openalex", "crossref", "zotero"}

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

    if not selected:
        return {"arxiv", "zbmath", "openalex", "crossref", "zotero"}

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

    JSON = get_JSON_from_zbmath(zbMATH)

    # Create or truncate the output file before running tests.
    with open("crossref.yaml", "w", encoding="utf-8"):
        pass

    for item in JSON["result"]:
        for link in item["links"]:
            if link["type"] == "doi":
                DOI = link["identifier"]
                try:
                    YAML = get_paper_YAML_from_crossref(DOI)
                    with open("crossref.yaml", "a", encoding="utf-8") as f:
                        f.write(YAML)
                        f.write("\n")
                except Exception as e:
                    print("YAML retrieval failed:", e, "\n")
                break

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
if __name__ == "__main__":
    main()