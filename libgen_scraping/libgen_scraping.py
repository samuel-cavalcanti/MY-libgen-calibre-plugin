from urllib import parse as url_parse

from bs4 import BeautifulSoup


class LibgenScraping:
    __soup: BeautifulSoup
    __min_tags = 17

    def __init__(self, html_page: str, base_url: str):
        self.__soup = BeautifulSoup(html_page, 'lxml')
        self.__base_url = base_url

    def scraping_books_meta_data(self):
        html_t_bodies = self.__soup.find_all('tbody')

        return self.__recovery_all_possible_book_metadata(html_t_bodies)

    def __recovery_all_possible_book_metadata(self, html_t_bodies):
        books = list()
        for t_body in html_t_bodies:
            if self.__possible_to_recovery(t_body):
                books.append(self.__recovery_meta_data_from_tbody_tag(t_body))

        return books

    def __possible_to_recovery(self, t_body_html_tag):
        return len(t_body_html_tag) >= self.__min_tags

    def __recovery_meta_data_from_tbody_tag(self, t_body_tag) -> dict:
        book_metadata = dict()
        book_metadata['Img'] = f'{self.__base_url}{t_body_tag.find("img").get("src")[1:]}'

        current_metadata = False
        for tr in t_body_tag.find_all('tr')[1:]:
            for td in tr.find_all('td'):
                if self.__have_nothing(td):  # have nothing
                    continue

                if td.attrs.get('rowspan', False):
                    book_metadata['Link'] = self.__base_url + td.find('a').attrs['href']
                    continue

                font_tag = td.find('font')
                if font_tag and font_tag.get('color') == 'gray':
                    current_metadata = td.getText().split(':')[0]
                elif current_metadata:
                    book_metadata[current_metadata] = td.getText()
                    current_metadata = False

        return book_metadata

    @staticmethod
    def __have_nothing(td_html_tag):
        return len(td_html_tag) == 0

    def __make_link(self, metadata: dict):

        file_name = self.__recovery_file_name_form_metadata(metadata)

        split_link = metadata['Link'].split('md5=')

        img_path = metadata['Img'].split(self.__base_url)[1]
        split_img_url = img_path.split('/')

        # print(f'{metadata["Link"]} {len(split_link)}', f'{split_img_url} {len(split_img_url)}')
        if self.__is_invalid_link(split_link, split_img_url):
            return

        md5 = split_link[1].lower()
        img_id = split_img_url[1]

        link = 'http://93.174.95.29/main/{}/{}/{}'.format(
            img_id, md5, url_parse.quote(file_name))

        return link

    @staticmethod
    def __is_invalid_link(split_link, split_img_url):
        return len(split_link) != 2 or len(split_img_url) != 3

    @staticmethod
    def __recovery_file_name_form_metadata(metadata: dict):
        file_name = ''

        if metadata.get('Series', False):
            file_name += '({}) '.format(metadata['Series'])

        if metadata.get('Author(s)', False):
            file_name += '{} - {}'.format(metadata['Author(s)'],
                                          metadata['Title'].replace(':', '_'))

        if metadata.get('Publisher', False):
            file_name += '-{}'.format(metadata['Publisher'])

        if metadata.get('Year', False) and metadata.get('Extension', False):
            file_name += ' ({}).{}'.format(metadata['Year'], metadata['Extension'])

        return file_name
