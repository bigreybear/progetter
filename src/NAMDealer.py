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
        # self.xpath_dic['href'] = '//div[@class="dir-member-name"]/a/@href'
        self.xpath_dic['name'] = '//div[@class="dir-member-details"]/h3'
        self.xpath_dic['year_selected'] = '//div[@class="member-info-section"]/div'
        # self.xpath_dic['citation'] = '//div[@class="member-details-text"]/p'
        self.xpath_dic['previous_service'] = '//div[@class="member-info-section"]/ul/li'
        self.xpath_dic['organization'] = '//div[@class="dir-member-details"]'

        self.selenium_dic = {}
        self.browser = None

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
                new_prf = self.single_page_by_selenium(purl)
                self.prf_list.append(new_prf)
                self.dict_printer(new_prf)
                logger.info("Processed {} / {} professors.".format(len(self.prf_list), len(self.url_list)))
                self.dealer_dump(prf_=True)
            self.dealer_dump(prf_=True, fin_=True)

        if self.browser is not None:
            self.browser.quit()
        return 0

    def selenium_worker(self, _start_url=""):
        """
        While there is anti-crawler strategy, we can get the content this way.
        :return:
        """
        browser = webdriver.Chrome()
        browser.get(_start_url)
        self.selenium_dic['next_button'] = '//*[@class="page-link next"]'
        self.selenium_dic['url_elem'] = '//*[@class="dir-member-name"]/a'
        tries = 0
        page_count = 1
        new_page = True  # Means info in this page had been processed.
        while tries < (self.max_retry+1):
            try:
                if new_page:
                    url_elems = browser.find_elements_by_xpath(self.selenium_dic['url_elem'])
                    next_elem = browser.find_element_by_xpath(self.selenium_dic['next_button'])
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
                    url_elems = browser.find_elements_by_xpath(self.selenium_dic['url_elem'])
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

    def single_page_by_selenium(self, _url):
        def get_elem_text(__xpath):
            return [x.text for x in self.browser.find_elements_by_xpath(__xpath)]
        _this_prf = {}
        try:
            if self.browser is None:
                self.browser = webdriver.Chrome()
            self.browser.get(_url)

            for key, value in self.xpath_dic.items():
                _this_prf[key] = "; ".join(get_elem_text(value))
                if key == "organization":
                    _this_prf[key] = _this_prf[key][_this_prf[key].find('\n')+1:]
                if key == "year_selected":
                    _this_prf["state"] = _this_prf[key][_this_prf[key].rfind(':')+2:]
                    _this_prf["year_selected"] = _this_prf[key][_this_prf[key].find(':') + 2:_this_prf[key].find(';')]

            return _this_prf
        except BaseException as e:
            logger.info(e.message)
            self.browser.quit()


if __name__ == '__main__':
    nam = NAMDealer()
    # nam.router({'phase': 1, 'url_rebuild_src': "tmp"})
    # nam.to_debug()
    # nam.selenium_worker("https://nam.edu/directory/?lastName=&firstName=&parentInstitution=&yearStart=&yearEnd=&presence=1")
    cmd = {'url_rebuild_src': "url_nam.tmp", 'phase': 2}
    nam.router(cmd)
    # nam.rebuild(url_="url_nam.tmp")