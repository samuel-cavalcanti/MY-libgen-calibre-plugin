import requests
import urllib
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
        self.base_url = "https://libgen.is"
        self.search_url = self.base_url + '/search.php?req='
        self.view_detailed = '&view=detailed'  # get image
        self.sorting_by_year = "&sort=year&sortmode=DESC"

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
            search_view_detailed_url = self.search_url + query_parsed + \
                '&column=title' + self.view_detailed + self.sorting_by_year
        elif self.search_type.lower() == 'author':
            search_view_detailed_url = self.search_url + query_parsed + \
                '&column=author' + self.view_detailed + self.sorting_by_year

        return requests.get(search_view_detailed_url)

    @staticmethod
    def scraping_mirrors_in_table(table):

        # Skip row 0 as it is the headings row
        for tr in table.find_all("tr")[1:]:
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
            for td in tr.find_all("td"):
                if len(td) == 0:  # have nothing
                    continue
                if td.attrs.get("rowspan", None):
                    table["Link"] = self.base_url + td.find("a").attrs["href"]
                    continue

                font_tag = td.find("font")
                if font_tag and font_tag.get("color") == "gray":
                    key = td.getText().split(":")[0]
                else:

                    table[key] = td.getText()

        table["Img"] = self.base_url + t_body_tag.find("img").get("src")

        encoded_table = {
            key.encode('utf-8', 'ignore'): table[key].encode('utf-8', 'ignore') for key in table}

        self.make_link(encoded_table)

        return encoded_table

    @staticmethod
    def make_link(table):

        file = str()

        if table.get("Series", False):
            file += "({}) ".format(table["Series"])

        file += "{} - {}".format(table["Author(s)"],
                                 table["Title"].replace(":", "_"))

        if table.get("Publisher", False):
            file += "-{}".format(table["Publisher"])

        if table.get("Year", False) and table.get("Extension", False):
            file += " ({}).{}".format(table["Year"], table["Extension"])
        else:
            for key in table:
                print(key, table[key])

        splitted_link = table["Link"].split("md5=")

        splitted_img_url = table["Img"].split("/")

        if len(splitted_link) != 2 or len(splitted_img_url) != 6:
            return

        md5 = splitted_link[1].lower()
        img_id = splitted_img_url[4]

        link = "http://93.174.95.29/main/{}/{}/{}".format(
            img_id, md5, urllib.quote(file))

        table["Mirrors"] = {table["Extension"].upper(): link}

    def scraping_detailed_view_data(self, search_page):

        soup = BeautifulSoup(search_page.text, "html5lib")
        # self.strip_i_tag_from_soup(soup)

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
                url_link = BeautifulSoup(
                    resp.text, "html").find("a", string="GET")
                if url_link:
                    downloads.append(url_link.attrs["href"])

        return downloads

    def aggregate_request_data(self):
        search_page_detailed = self.get_search_page()

        t_body_iter = self.scraping_detailed_view_data(search_page_detailed)

        # mirrors_iter = self.scraping_simple_view_data(search_page_simple)

        return self.get_download_link_and_formatting_data(t_body_iter)

    def aggregate_request_data_iter(self):
        search_page_detailed = self.get_search_page()

        t_body_iter = self.scraping_detailed_view_data(search_page_detailed)

        return t_body_iter


class LibgenSearch:

    @staticmethod
    def search_title(query):
        search_request = SearchRequest(query, search_type="title")
        return search_request.aggregate_request_data()

    @staticmethod
    def search_title_iter(query):
        search_request = SearchRequest(query, search_type="title")
        return search_request.aggregate_request_data_iter()

    @staticmethod
    def search_author(query):
        search_request = SearchRequest(query, search_type="author")
        return search_request.aggregate_request_data()

    @staticmethod
    def search_author_iter(query):
        search_request = SearchRequest(query, search_type="author")
        return search_request.aggregate_request_data_iter()

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
            filtered_data = [
                d for d in filtered_data if d[f] in filters.values()]
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
            filtered_data = [
                d for d in filtered_data if d[f] in filters.values()]
        return filtered_data


def test_libgen():
    libgen_search = LibgenSearch()
    libgen_results = libgen_search.search_author("eduardo moreira")

    for result in libgen_results:

        link = str()

        if result.get("Series", "") != "":
            link += "({}) ".format(result["Series"])

        link += "{} - {}".format(result["Author(s)"],
                                 result["Title"].replace(":", "_"))

        if result.get("Publisher", "") != "":
            link += "-{}".format(result["Publisher"])

        # link += " ({}).{}".format(result["Year"], result["Extension"])

        print(link)

        pass


if __name__ == '__main__':
    test_libgen()
   
