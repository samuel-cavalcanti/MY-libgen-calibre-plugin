import unittest

from libgen_query.libgen_search_query import LibgenSearchQuery


class MyTestCase(unittest.TestCase):
    def test_title_search_query(self):
        eduardo_query = LibgenSearchQuery("eduardo moreira", "http://libgen.rs/",
                                          LibgenSearchQuery.TITLE_SEARCH)

        sinais_query = LibgenSearchQuery("sinais e sistemas", "http://libgen.rs/",
                                         LibgenSearchQuery.TITLE_SEARCH)

        expect_eduardo_url = 'http://libgen.rs//search.php?req=eduardo%20moreira&view=detailed&phrase=1&&sort=year&sortmode=DESC&column=title'
        expect_sinais_url = 'http://libgen.rs//search.php?req=sinais%20e%20sistemas&view=detailed&phrase=1&&sort=year&sortmode=DESC&column=title'

        self.assertEqual(eduardo_query.to_url(), expect_eduardo_url)
        self.assertEqual(sinais_query.to_url(), expect_sinais_url)

    def test_author_search_query(self):
        eduardo_query = LibgenSearchQuery("eduardo moreira", "http://libgen.rs/",
                                          LibgenSearchQuery.AUTHOR_SEARCH)

        sinais_query = LibgenSearchQuery("sinais e sistemas", "http://libgen.rs/",
                                         LibgenSearchQuery.AUTHOR_SEARCH)

        expect_eduardo_url = 'http://libgen.rs//search.php?req=eduardo%20moreira&view=detailed&phrase=1&&sort=year&sortmode=DESC&column=author'
        expect_sinais_url = 'http://libgen.rs//search.php?req=sinais%20e%20sistemas&view=detailed&phrase=1&&sort=year&sortmode=DESC&column=author'

        self.assertEqual(eduardo_query.to_url(), expect_eduardo_url)
        self.assertEqual(sinais_query.to_url(), expect_sinais_url)

    def test_default_search_query(self):
        eduardo_query = LibgenSearchQuery("eduardo moreira", "http://libgen.rs/",
                                          LibgenSearchQuery.DEFAULT_SEARCH)

        sinais_query = LibgenSearchQuery("sinais e sistemas", "http://libgen.rs/",
                                         LibgenSearchQuery.DEFAULT_SEARCH)

        expect_eduardo_url = 'http://libgen.rs//search.php?req=eduardo%20moreira&view=detailed&phrase=1&&sort=year&sortmode=DESC&column=def'
        expect_sinais_url = 'http://libgen.rs//search.php?req=sinais%20e%20sistemas&view=detailed&phrase=1&&sort=year&sortmode=DESC&column=def'

        self.assertEqual(eduardo_query.to_url(), expect_eduardo_url)
        self.assertEqual(sinais_query.to_url(), expect_sinais_url)


if __name__ == '__main__':
    unittest.main()
