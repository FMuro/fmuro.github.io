import unittest
from unittest.mock import patch

from arxiv import get_JSON_from_arXiv_paper


class GetJsonFromArxivPaperTests(unittest.TestCase):
    def test_returns_feed_data_for_a_paper_id(self):
        sample_payload = {"entries": [{"id": "http://arxiv.org/abs/2401.00001"}]}

        with patch("arxiv.feedparser.parse", return_value=sample_payload) as parse_mock:
            result = get_JSON_from_arXiv_paper("arXiv:2401.00001")

        parse_mock.assert_called_once()
        self.assertEqual(result, sample_payload)


if __name__ == "__main__":
    unittest.main()
