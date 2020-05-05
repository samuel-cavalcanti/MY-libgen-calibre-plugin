import requests
from bs4 import BeautifulSoup


# WHY
# this SearchRequest module is used to contain all of the internal logic that end users will not need to use.
# Therefore the logic is contained and users can interact with libgen_search without extra junk for logic.

# USAGE
# req = search_request.SearchRequest("[QUERY]", search_type="[title]")

class SearchRequest:
    __min_tags = 17

    def __init__(self, query, search_type="title"):
        self.query = query
        self.search_type = search_type
        self.base_url = "http://gen.lib.rus.ec"
        self.search_url = self.base_url + '/search.php?req='
        self.view_detailed = '&view=detailed'  # get image

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

    # TODO
    # def get_search_page(self):
    #     query_parsed = "%20".join(self.query.split(" "))
    #     if self.search_type.lower() == 'title':
    #         search_view_simple_url = self.search_url + query_parsed + '&column=title'
    #         search_view_detailed_url = self.search_url + query_parsed + '&column=title' + self.view_detailed
    #     elif self.search_type.lower() == 'author':
    #         search_view_simple_url = self.search_url + query_parsed + '&column=author'
    #         search_view_detailed_url = self.search_url + query_parsed + '&column=author' + self.view_detailed
    #
    #     return requests.get(search_view_simple_url), requests.get(search_view_detailed_url)

    def get_search_page(self):
        query_parsed = "%20".join(self.query.split(" "))
        if self.search_type.lower() == 'title':
            search_view_detailed_url = self.search_url + query_parsed + '&column=title' + self.view_detailed
        elif self.search_type.lower() == 'author':
            search_view_detailed_url = self.search_url + query_parsed + '&column=author' + self.view_detailed

        return requests.get(search_view_detailed_url)

    @staticmethod
    def scraping_mirrors_in_table(table):

        for tr in table.find_all("tr")[1:]:  # Skip row 0 as it is the headings row
            mirrors = list()
            for td in tr.find_all("td"):
                a = td.find('a')
                if a and a.attrs.get("title", "") != "":
                    text = td.getText()
                    if text != "[edit]":
                        mirrors.append(td.a["href"])

            yield mirrors

    def scraping_simple_view_data(self, search_page):

        soup = BeautifulSoup(search_page.text, 'lxml')
        self.strip_i_tag_from_soup(soup)

        # Libgen results contain 3 tables
        # Table2: Table of data to scrape.
        information_table = soup.find_all('table')[2]

        return self.scraping_mirrors_in_table(information_table)

    def scraping_tbody_tag(self, t_body_tag):

        table = dict()
        for tr in t_body_tag.find_all("tr")[1:]:
            td_it = iter(tr.find_all("td"))
            td = next(td_it, None)
            while td is not None:
                font_tag = td.find("font")
                if font_tag and font_tag.get("color") == "gray":
                    key = td.getText().split(":")[0]
                    td = next(td_it, None)
                    pass
                else:
                    value = td.getText()
                    if value != "":
                        table[key] = value

                    if td.attrs.get("rowspan", None):
                        table["Link"] = self.base_url + td.find("a").attrs["href"]

                    td = next(td_it, None)
        table["Img"] = self.base_url + t_body_tag.find("img").get("src")

        return table

    def scraping_detailed_view_data(self, search_page):

        soup = BeautifulSoup(search_page.text, 'lxml')
        self.strip_i_tag_from_soup(soup)

        print("numbers of tbody", len(soup.find_all("tbody")))
        for tbody in soup.find_all("tbody"):
            if len(tbody) >= self.__min_tags:
                yield self.scraping_tbody_tag(tbody)

    def get_download_link_and_formatting_data(self, t_body_it):
        raw_data = next(t_body_it, None)
        output_data = list()

        while raw_data is not None:
            output_data.append(raw_data)
            raw_data = next(t_body_it, None)

        return output_data

    def mirros_to_download_link(self, mirrors):
        downloads = list()
        for mirror in mirrors:
            resp = requests.get(mirror)
            if 199 < resp.status_code < 300:
                url_link = BeautifulSoup(resp.text, "lxml").find("a", string="GET")
                if url_link:
                    downloads.append(url_link.attrs["href"])

        return downloads

    def aggregate_request_data(self):
        search_page_detailed = self.get_search_page()

        t_body_iter = self.scraping_detailed_view_data(search_page_detailed)

        # mirrors_iter = self.scraping_simple_view_data(search_page_simple)

        return self.get_download_link_and_formatting_data(t_body_iter)


class LibgenSearch:

    def search_title(self, query):
        self.search_request = SearchRequest(query, search_type="title")
        return self.search_request.aggregate_request_data()

    def search_author(self, query):
        self.search_request = SearchRequest(query, search_type="author")
        return self.search_request.aggregate_request_data()

    def search_title_filtered(self, query, filters=None):
        if filters is None:
            filters = {"ID": "",
                       "Author(s)": "",
                       "Title": "",
                       "Publisher": "",
                       "Year": "",
                       "Pages": "",
                       "Language": "",
                       "Size": "",
                       "Extension": "",
                       "Img": ""
                       }
        self.search_request = SearchRequest(query, search_type="title")
        data = self.search_request.aggregate_request_data()

        filtered_data = data
        for f in filters:
            filtered_data = [d for d in filtered_data if d[f] in filters.values()]
        return filtered_data

    def search_author_filtered(self, query, filters=None):
        if filters is None:
            filters = {"ID": "",
                       "Author": "",
                       "Title": "",
                       "Publisher": "",
                       "Year": "",
                       "Pages": "",
                       "Language": "",
                       "Size": "",
                       "Extension": "",
                       "Mirrors": [],
                       "Img": ""
                       }
        self.search_request = SearchRequest(query, search_type="author")
        data = self.search_request.aggregate_request_data()

        filtered_data = data
        for f in filters:
            filtered_data = [d for d in filtered_data if d[f] in filters.values()]
        return filtered_data


def test_libgen():
    libgen_search = LibgenSearch()
    libgen_results = libgen_search.search_title("way kings")

    for result in libgen_results:
        for key in result:
            print(key + ":", result[key])

        pass


def compress_files():
    import zipfile
    import os
    name_file = "libgen.zip"

    print("zipping!")
    if os.path.isfile(name_file):
        os.remove(name_file)
    zf = zipfile.ZipFile(name_file, "w", zipfile.ZIP_DEFLATED)

    zf.write("libgen.py")
    zf.write("__init__.py")

    print("Done")


if __name__ == '__main__':
    # test_libgen()
    compress_files()
