# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, division,
                        absolute_import, print_function)

from PyQt5.Qt import QUrl
from calibre.customize import StoreBase
from calibre.gui2 import open_url
from calibre.gui2.store import StorePlugin
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.web_store_dialog import WebStoreDialog

from libgen_search import LibgenSearch

store_version = 5  # Needed for dynamic plugin loading

__license__ = 'MIT'

#####################################################################
# Plug-in base class
#####################################################################

PLUGIN_NAME = 'Libgen'
PLUGIN_DESCRIPTION = 'Adds a Libgen search provider to Calibre'
PLUGIN_VERSION_TUPLE = (0, 1, 2)
PLUGIN_VERSION = '.'.join([str(x) for x in PLUGIN_VERSION_TUPLE])
PLUGIN_AUTHORS = "Samuel Cavalcanti (https://github.com/samuel-cavalcanti/MY-libgen-calibre-plugin)"


#####################################################################


class LibgenStore(StorePlugin):
    def search(self, query, max_results=1, timeout=120):
        search = LibgenSearch()
        print("Query:", query)

        result_of_scraping = search.default_search(query)

        for book in result_of_scraping:
            yield self.to_search_result(book)

    @staticmethod
    def to_search_result(book):
        s = SearchResult()

        s.store_name = "Libgen"
        s.title = book.get("Title", " ")
        s.author = book.get("Author(s)", " ")
        s.price = "FREE!!"
        s.language = book.get("Language", " ")
        s.downloads = book.get("Mirrors", " ")
        s.formats = book.get("Extension", " ")
        s.drm = SearchResult.DRM_UNLOCKED
        s.cover_url = book.get("Img", " ")
        s.detail_item = book.get("Link", " ")

        return s

    def open(self, gui, detail_item=None, external=False, parent=None):
        url = "https://libgen.is"

        if external:
            if detail_item:
                open_url(QUrl(detail_item))
            else:
                open_url(QUrl(url))

        else:
            d = WebStoreDialog(self.gui, detail_item)
            d.setWindowTitle(self.name)
            d.exec_()


class LibgenStoreWrapper(StoreBase):
    name = PLUGIN_NAME
    description = PLUGIN_DESCRIPTION
    supported_platforms = ['windows', 'osx', 'linux']
    author = PLUGIN_AUTHORS
    version = PLUGIN_VERSION_TUPLE
    minimum_calibre_version = (1, 0, 0)
    affiliate = False

    def load_actual_plugin(self, gui):
        '''
        This method must return the actual interface action plugin object.
        '''
        # mod, cls = self.actual_plugin.split(':')
        store = LibgenStore(gui, self.name)
        # getattr(importlib.import_module(mod), cls)(gui, self.name)
        self.actual_plugin_object = store
        return self.actual_plugin_object
