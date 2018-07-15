#!/usr/bin/env python
# -*- coding: utf-8 -*-
from loggetter import logger
import lxml.etree as etree
from src.AbsDealer import AbsDealer as AD
from src.AbsDealer import LAST_PAGE, ERROR_PAGE, NORMAL_PAGE, POST, GET
import urllib2
import urllib
import time
from selenium import webdriver
import socket


class NAMDealer(AD):
    def __init__(self):
        AD.__init__(self)
        self.header = {
            'POST': "/wp-content/themes/NAMTheme/directory/index.php HTTP/1.1",
            'Host': "nam.edu",
            'Connection': "keep-alive",
            'Content-Length': "27",
            'Accept': "*/*",
            'Origin': "https://nam.edu",
            'X-Requested-With': "XMLHttpRequest",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'DNT': "1",
            'Referer': "https://nam.edu/directory/?lastName=&firstName=&parentInstitution=&yearStart=&yearEnd=&presence=1",
            'Accept-Encoding': "utf-8",
            'Accept-Language': "en",
            'Cookie': "PHPSESSID=0af4ccb79dd34cbbe5c882d520353588; _ga=GA1.2.1390685861.1531564907; _gid=GA1.2.334374399.1531564907; __qca=P0-1027726874-1531564908621; __atuvc=5%7C28; __atuvs=5b49d383a698a885004"
        }

        self.page_prefix = "https://nam.edu/directory/?lastName=&firstName=&parentInstitution=" \
                           "&yearStart=&yearEnd=&presence=1#page-1"
        self.xpath_dic['href'] = '//div[@class="dir-member-name"]/a/@href'
        self.xpath_dic['name'] = '//div[@class="member-details-wrap"]/h1'
        self.xpath_dic['year_selected'] = '//div[@class="member-sml-details hidden-sm hidden-xs"]/p'
        self.xpath_dic['citation'] = '//div[@class="member-details-text"]/p'

        self.tmp_save_name = "nam.tmp"
        self.fin_save_name = "nam.bin"
        self.person_page_root = "https://www.science.org.au/"
        self.current_page = ""
        self.valve = 50
        self.timeout = 5
        self.max_retry = 8
        self.interval_time = 3

    def one_page_pros(self, content_=None):
        # In AAS, you need pick all urls of personal page first.
        if content_ is None:
            content_ = self.pros_page(self.page_prefix)
        tree = etree.HTML(content_)
        hrefs = tree.xpath(self.xpath_dic['href'])
        print(len(hrefs))
        for href in hrefs:
            self.url_list.append(href.encode('utf-8'))
        if len(hrefs) != 0:
            logger.info("Its a normal page and {} data accumulated.".format(len(self.url_list)))
            return NORMAL_PAGE
        else:
            return ERROR_PAGE

    def router(self, cmds=None):
        if cmds is None:
            cmds = {'phase': -1}
        if (cmds['phase'] == 1) or (cmds['phase'] == 0):
            # ***** ***** ***** ***** #
            # PHASE ONE: GET ALL URLS #
            # ***** ***** ***** ***** #
            url_page_count = 1
            self.current_page = "https://nam.edu/directory/?lastName=&firstName=&parentInstitution=&yearStart=&yearEnd=&presence=1#page-{}".format(url_page_count)
            while self.one_page_pros(self.pros_page(self.current_page)) == NORMAL_PAGE:
                url_page_count += 1
                self.current_page = "https://nam.edu/directory/?lastName=&firstName=&parentInstitution=" \
                                    "&yearStart=&yearEnd=&presence=1#page-{}".format(url_page_count)
                self.dealer_dump(url_=True)
            self.dealer_dump(url_=True, fin_=True)

        if (cmds['phase'] == 2) or (cmds['phase'] == 0):

            # ***** ***** ***** ***** ***#
            # PHASE TWO: REBUILD AND GET #
            # ***** ***** ***** ***** ***#
            self.rebuild(url_=cmds['url_rebuild_src'])
            for purl in self.url_list:
                self.personal_page("{}/{}".format(self.person_page_root, purl))
                self.dealer_dump(prf_=True)
            self.dealer_dump(prf_=True, fin_=True)
        return 0

    def personal_page(self, url_=None):
        if url_ is None:
            content_ = self.pros_page(self.page_prefix)
        else:
            content_ = self.pros_page(url_)
        tree = etree.HTML(content_)
        data_ = {}
        for key, value in self.xpath_dic.items():
            if len(tree.xpath(value)) == 1:
                data_[key] = tree.xpath(value)[0].text.encode('utf-8')
            else:
                for e_part in tree.xpath(value):
                    if e_part.text is not None:
                        data_[key] = e_part.text.encode('utf-8')
        self.dict_printer(data_)
        self.prf_list.append(data_)
        logger.info("Accumulated {} data.".format(len(self.prf_list)))

    def to_debug(self):

        browser = webdriver.Chrome()
        browser.get("https://nam.edu/directory/?lastName=&firstName=&parentInstitution=&yearStart=&yearEnd=&presence=1")
        xpath = '//*[@class="page-link next"]'
        xpath_a = '//*[@class="dir-member-name"]/a'
        for tries in range(self.max_retry):
            try:
                el1 = browser.find_element_by_xpath(xpath)
                el2 = browser.find_element_by_xpath(xpath_a)
            except BaseException as e:
                if tries < (self.max_retry - 1):
                    time.sleep(self.interval_time)
                    logger.info("{}...".format(tries))
                    continue
                else:
                    raise e

        print(el2)
        el1.click()
        try:
            elem = browser.find_element_by_xpath(xpath)
        except BaseException:
            logger.info("No more Next.")
            browser.quit()
            return
        return

    def pros_page(self, url=None, method_=GET, data_=None):
        logger.info("Test pros_page.")
        if url is None:
            url = self.page_prefix
        _content = None
        if method_ == POST:
            if data_ is None:
                logger.error("No data for POST request for {}.".format(url))
            else:
                # actually run code
                data_ = urllib.urlencode(data_)
                _req = urllib2.Request(url, headers=self.header, data=data_)
                logger.info("Formed a POST request for url: {}".format(_req.data))
        else:
            _req = urllib2.Request(url, headers=self.header)
            logger.info("Formed a GET request for url: {}".format(_req))

        for tries in range(self.max_retry):
            try:
                time.sleep(self.interval_time)
                logger.info("Start to open...")
                _content = urllib2.urlopen(_req, timeout=self.timeout * 1000, data=data_)
                break
            except BaseException as e:
                if tries < (self.max_retry - 1):
                    logger.error("Catch a exception of {}.".format(e.message))
                    logger.error("Connection failed, try {} time(s), at url: {}".format(tries, url))
                    continue
                else:
                    logger.error("Tried {} times to connect url:{}, but failed.".format(self.max_retry, url))
                    logger.error(e.message)
                    exit()
        _ret = _content.read()
        _content.close()
        logger.debug("Processing url: {}".format(url))
        return _ret

    def selenium_worker(self, _start_url=""):
        """
        While there is anti-crawler strategy, we can get the content this way.
        :return:
        """
        browser = webdriver.Chrome()
        browser.get(_start_url)
        self.xpath_dic['next_button'] = '//*[@class="page-link next"]'
        self.xpath_dic['url_elem'] = '//*[@class="dir-member-name"]/a'
        tries = 0
        page_count = 1
        new_page = True  # Means info in this page had been processed.
        while tries < (self.max_retry+1):
            try:
                if new_page:
                    url_elems = browser.find_elements_by_xpath(self.xpath_dic['url_elem'])
                    next_elem = browser.find_element_by_xpath(self.xpath_dic['next_button'])
                    if next_elem is None:
                        logger.info("Finally finished.")
                        self.dealer_dump(True, False, True)
                        break
                    for elem in url_elems:
                        self.url_list.append(elem.get_attribute("href"))

                    logger.info("Finished page {}, {} urls had been recorded.".format(page_count, len(self.url_list)))
                    new_page = False
                    url_elems = None

                if not new_page:
                    if url_elems is None:
                        next_elem.click()  # Means only click "ONCE"
                    time.sleep(1)
                    url_elems = browser.find_elements_by_xpath(self.xpath_dic['url_elem'])
                    # logger.info(url_elems)
                    if len(url_elems) != 0:
                        new_page = True
                        page_count += 1
                        tries = 0
            except BaseException as e:
                tries += 1
                time.sleep(self.timeout)
                if tries >= self.max_retry:
                    logger.info("Tried too many times, and we got at this page: X")
                    self.dealer_dump(True)
                    print(e.message)
                    raise e
                else:
                    logger.info("Trid for {} time(s) at page {}.".format(tries, page_count))
                    continue
        browser.quit()
        return

if __name__ == '__main__':
    nam = NAMDealer()
    # nam.router({'phase': 1, 'url_rebuild_src': "tmp"})
    # nam.to_debug()
    nam.selenium_worker("https://nam.edu/directory/?lastName=&firstName=&parentInstitution=&yearStart=&yearEnd=&presence=1")
