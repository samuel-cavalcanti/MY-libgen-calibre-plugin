import json
import unittest

from libgen_scraping.libgen_scraping import LibgenScraping


class MyTestCase(unittest.TestCase):

    @staticmethod
    def __load_local_response() -> str:
        with open('response.html') as file:
            return file.read()

    @staticmethod
    def __load_expected_output():
        with open('expect_output.json') as file:
            return list(json.load(file))

    def test_something(self):
        response = self.__load_local_response()
        expected_output = self.__load_expected_output()
        base_url = 'http://gen.lib.rus.ec/'
        scraping = LibgenScraping(response, base_url)
        books = scraping.scraping_books_meta_data()

        self.assertEqual(books, expected_output)


if __name__ == '__main__':
    unittest.main()
