import unittest
import warnings
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Code.recommenderapp.search import Search

warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):
    def setUp(self):
        self.search = Search()
        
    def test_search_toy(self):
        search_word = "toy"
        filtered_dict = self.search.resultsTop10(search_word)
        expected_resp = [
            "Toy Story (1995)",
            "Toys (1992)",
            "Toy Story 2 (1999)",
            "Toy, The (1982)",
            "Toy Soldiers (1991)",
            "Toy Story 3 (2010)",
            "Babes in Toyland (1961)",
            "Babes in Toyland (1934)",
        ]
        self.assertEqual(filtered_dict, expected_resp)

    def test_search_love(self):
        search_word = "love"
        filtered_dict = self.search.resultsTop10(search_word)
        expected_resp = [
            "Love & Human Remains (1993)",
            "Love Affair (1994)",
            "Love and a .45 (1994)",
            "Love in the Afternoon (1957)",
            "Love Bug, The (1969)",
            "Love Jones (1997)",
            "Love and Other Catastrophes (1996)",
            "Love Serenade (1996)",
            "Love and Death on Long Island (1997)",
            "Love Is the Devil (1998)",
        ]
        self.assertEqual(filtered_dict, expected_resp)

    def test_search_gibberish(self):
        search_word = "gibberish"
        filtered_dict = self.search.resultsTop10(search_word)
        expected_resp = []
        self.assertEqual(filtered_dict, expected_resp)

    def test_search_1995(self):
        search_word = "1995"
        filtered_dict = self.search.resultsTop10(search_word)
        expected_resp = [
            "Toy Story (1995)",
            "Jumanji (1995)",
            "Grumpier Old Men (1995)",
            "Waiting to Exhale (1995)",
            "Father of the Bride Part II (1995)",
            "Heat (1995)",
            "Sabrina (1995)",
            "Tom and Huck (1995)",
            "Sudden Death (1995)",
            "GoldenEye (1995)",
        ]
        self.assertEqual(filtered_dict, expected_resp)


if __name__ == "__main__":
    unittest.main()
