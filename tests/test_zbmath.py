import unittest
from unittest.mock import patch

from zbmath import get_author_from_id, get_author_lookup_from_zbmath


class GetAuthorFromIdTests(unittest.TestCase):
    def test_returns_renamed_spelling_fields(self):
        sample_response = {
            "result": {
                "spellings": [
                    {
                        "first_name": "Fernando",
                        "last_name": "Muro",
                        "name": "Muro, Fernando",
                        "count": 36,
                    }
                ]
            }
        }

        with patch("zbmath._read_json_response", return_value=sample_response):
            self.assertEqual(
                get_author_from_id("muro.fernando"),
                {"given": "Fernando", "family": "Muro"},
            )

    def test_returns_empty_dict_when_no_spellings(self):
        with patch("zbmath._read_json_response", return_value={"result": {}}):
            self.assertEqual(get_author_from_id("muro.fernando"), {})

    def test_builds_lookup_from_unique_author_codes(self):
        sample_payload = {
            "result": [
                {
                    "contributors": {
                        "authors": [
                            {"codes": ["muro.fernando"]},
                            {"codes": ["jasso.gustavo", "muro.fernando"]},
                        ]
                    }
                },
                {
                    "contributors": {
                        "authors": [{"codes": ["keller.bernhard"]}]
                    }
                },
            ]
        }

        with patch("zbmath.get_author_from_id", side_effect=lambda code: {"given": code, "family": code}):
            result = get_author_lookup_from_zbmath(sample_payload)

        self.assertEqual(
            result,
            {
                "muro.fernando": {"given": "muro.fernando", "family": "muro.fernando"},
                "jasso.gustavo": {"given": "jasso.gustavo", "family": "jasso.gustavo"},
                "keller.bernhard": {"given": "keller.bernhard", "family": "keller.bernhard"},
            },
        )


if __name__ == "__main__":
    unittest.main()
