import requests

from libgen_query.libgen_search_query import LibgenSearchQuery
from libgen_scraping.libgen_scraping import LibgenScraping


class LibgenSearch:
    __libgen_base_urls = ['http://gen.lib.rus.ec/', 'http://libgen.rs/', 'http://libgen.gs/ ']

    def search_title(self, query: str):
        libgen_query = LibgenSearchQuery(query, base_url=self.__libgen_base_urls[0],
                                         search_type=LibgenSearchQuery.TITLE_SEARCH)

        return self.__searching_in_libgen(libgen_query)

    def search_author(self, query: str):
        libgen_query = LibgenSearchQuery(query, base_url=self.__libgen_base_urls[0],
                                         search_type=LibgenSearchQuery.AUTHOR_SEARCH)
        return self.__searching_in_libgen(libgen_query)

    def default_search(self, query: str):
        libgen_query = LibgenSearchQuery(query, base_url=self.__libgen_base_urls[0])

        return self.__searching_in_libgen(libgen_query)

    @staticmethod
    def __searching_in_libgen(libgen_query: LibgenSearchQuery):
        request = requests.get(libgen_query.to_url())
        libgen_scraping = LibgenScraping(request.text)
        result_of_scraping = libgen_scraping.scraping_books_meta_data()
        return result_of_scraping
