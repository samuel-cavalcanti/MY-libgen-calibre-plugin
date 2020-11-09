import urllib.parse


class LibgenSearchQuery:
    __query: str
    __base_url: str
    __search_type: int
    __search_path = 'search.php?req='
    DEFAULT_SEARCH = 0
    TITLE_SEARCH = 1
    AUTHOR_SEARCH = 2
    SERIES_SEARCH = 3
    __search_in_fields = {
        0: 'def',
        1: 'title',
        2: 'author',
        3: 'series'
    }

    def __init__(self, calibre_query: str, base_url: str, search_type=0):
        self.__query = calibre_query
        self.__base_url = base_url
        self.__search_type = self.__search_in_fields.get(search_type, 0)

    def to_url(self) -> str:
        parsed_query = urllib.parse.quote(self.__query)
        # 'view=detailed', because this param it's possible get the book thumbnail and download link
        view_query_param = 'view=detailed&phrase=1&'
        sorting_by_year = 'sort=year&sortmode=DESC'
        search_in_fields_param = f'column={self.__search_type}'
        return f'{self.__base_url}/{self.__search_path}{parsed_query}&' \
               f'{view_query_param}&{sorting_by_year}&{search_in_fields_param}'
