import urllib2
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from bs4 import NavigableString
import pickle
import copy


class AbsDealer:
    def __init__(self):
        self.header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/64.0.3282.119 Safari/537.36"}
        self.is_debug = False
        self.interval_time = 5
        self.timeout = 40
        self.request_prefix = ""
        self.tmp_save_name = ""
        self.nas_page_list = []
        self.nas_page_list_save_name = ""
        self.url_list = None
        self.failed_list = []

        # page_prefix is the main crawl page root, crawler start here.
        self.page_prefix = ""
        # crawl counter.
        self.cnt = 0
        # professor data list, each of which is a dictionary.
        self.prf_list = []
        pass

    def pros_page(self, url=None):
        """
        To get the content of a page of pros, without deal it with bs4, without construct url itself.
        :param url: The fetch url.
        :return:
        """

    def router(self, cmd=None):
        """
        Core method to Control how to get every professor's personal page.
        Need to construct url for every @method:pros_page.
        :param cmd: K-V commands to control the router, according to different website.
        :return:
        """

    def one_page_pros(self, url=None):
        """
        To deal a page of pros, get every professor's personal page url and pass it (if necessary).

        :param url:
        :return:
        """
