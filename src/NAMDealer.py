#!/usr/bin/env python
# -*- coding: utf-8 -*-
from loggetter import logger
import lxml.etree as etree
from src.AbsDealer import AbsDealer as AD
from src.AbsDealer import LAST_PAGE, ERROR_PAGE, NORMAL_PAGE, POST, GET
import urllib2
import urllib
import time
import socket


class NAMDealer(AD):
    def __init__(self):
        AD.__init__(self)
        self.header = {
            'Accept': "*/*",
            'Accept-Encoding': "utf-8",
            'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,es;q=0.6,zh-TW;q=0.5",
            'Connection': "keep-alive",
            'Content-Length': "144",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Cookie': "PHPSESSID=8c85983495fb2cd211785c026dae8bbe; _ga=GA1.2.1003375805.1528273268; _gid=GA1.2.1678407113.1528273268; wordpress_test_cookie=WP+Cookie+check; __qca=P0-28642638-1528273288115; __atuvc=10%7C23",
            'DNT': "1",
            'Host': "nam.edu",
            'Origin': "https://nam.edu",
            'Referer': "https://nam.edu/directory/?lastName=&firstName=&parentInstitution=&yearStart=&yearEnd=&presence=1",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/66.0.3359.181 Safari/537.36",
            'X-Requested-With': "XMLHttpRequest"
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
        target_url = "https://nam.edu/wp-content/themes/NAMTheme/directory/index.php"
        form_data = {'page': 1, 'orderBy': 1, 'presence': 1}
        c_ = self.pros_page(target_url, POST, form_data)
        print(c_)
        print(type(c_))
        print(dict(c_))
        # print(chardet.detect(c_))
        # self.one_page_pros(c_)
        # c_ = self.pros_page(target_url)
        # self.one_page_pros(target_url)
        # for i in self.url_list:
        #     print(i)
        # self.personal_page("https://www.science.org.au///fellowship/fellows/professor-geordie-williamson")

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
                _content = urllib2.urlopen(_req, timeout=self.timeout * 1000, data=data_)
                break
            except urllib2.URLError, socket.error:
                if tries < (self.max_retry - 1):
                    continue
                else:
                    logger.error("Tried {} times to connect url:{}, but failed.".format(self.max_retry, url))
                    raise urllib2.URLError
        _ret = _content.read()
        _content.close()
        logger.debug("Processing url: {}".format(url))
        return _ret


if __name__ == '__main__':
    nam = NAMDealer()
    # nam.router({'phase': 1, 'url_rebuild_src': "tmp"})
    nam.to_debug()

