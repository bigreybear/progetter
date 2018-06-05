import json
import logging
from bs4 import BeautifulSoup
from loggetter import logger
import urllib2
import urllib
import lxml
import lxml.html as HTML
import lxml.etree as etree
from src.AbsDealer import AbsDealer as AD

# To note the router-profs page flag.
LAST_PAGE = -1
ERROR_PAGE = 0
NORMAL_PAGE = 1


class RSCDealer(AD, object):
    def __init__(self):
        AD.__init__(self)
        self.page_prefix = "http://www.rsc.ca/en/search-fellows"
        self.xpath_dic['pro'] = '//div[@class="row-wrapper"]'
        self.xpath_dic['name'] = './div[@class="views-field views-field-display-name"]/h3'
        self.xpath_dic['affiliation'] = './div[@class="views-field views-field-current-employer"]/span'
        self.xpath_dic['academy'] = './div[@class="views-field views-field-academy-25"]/span'
        self.xpath_dic['year_selected'] = './div[@class="views-field views-field-election-year-21"]/span'
        self.xpath_dic['discipline'] = './div[@class="views-field views-field-discipline-23"]/span'

        # NOT every website could get next page this way, so not in AbsDealer.
        self.xpath_next = '//li[@class="pager-next"]/a/@href'
        self.next_url = None

        # to complete the next page url in this website
        self.next_url_head = 'http://www.rsc.ca'
        pass

    def pros_page(self, url=None):
        if url is None:
            url = self.page_prefix
        _req = urllib2.Request(url, headers=self.header)
        _content = urllib2.urlopen(_req, timeout=self.timeout*1000)
        _ret = _content.read()
        _content.close()
        statement_ = "Processing url: {}".format(url)
        logger.debug(statement_)
        return _ret

    def one_page_pros(self, content_=None):
        # RSC has only a card for every professor, so it can make it can pick data here to list.
        tree = etree.HTML(content_)
        self.next_url = tree.xpath(self.xpath_next)
        # To judge if the last page
        if len(self.next_url) == 0:
            self.next_url = None
        else:
            self.next_url = self.next_url_head + self.next_url[0]
        all_prof_this_page = tree.xpath('//div[@class="row-wrapper"]')
        if len(all_prof_this_page) == 0:
            return ERROR_PAGE
        for prof in all_prof_this_page:
            data = {}
            for key, value in self.xpath_dic.items():
                if len(prof.xpath(value)) == 1:
                    data[key] = prof.xpath(value)[0].text
            self.prf_list.append(data)
            self.dict_printer(data)
        if self.next_url is None:
            return LAST_PAGE
        return NORMAL_PAGE

    def router(self, cmds=None):
        current_page = self.page_prefix
        while self.one_page_pros(self.pros_page(current_page)) == NORMAL_PAGE:
            current_page = self.next_url
        pass


if __name__ == '__main__':
    rsc = RSCDealer()
    # rsc.one_page_pros(rsc.pros_page())
    print rsc.one_page_pros(rsc.pros_page("http://www.rsc.ca/en/search-fellows?page=199"))
    print rsc.next_url
