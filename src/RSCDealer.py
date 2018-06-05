import json
import logging
from bs4 import BeautifulSoup
from loggetter import logger
import urllib2
import urllib
from src.AbsDealer import AbsDealer as AD


class RSCDealer(AD, object):
    def __init__(self):
        AD.__init__(self)
        self.page_prefix = "http://www.rsc.ca/en/search-fellows"
        pass

    def pros_page(self, url=None):
        if url is None:
            url = self.page_prefix
        _req = urllib2.Request(url, headers=self.header)
        _content = urllib2.urlopen(_req)

        logger.debug("Fetched web content")
        return _content.read()

    def router(self, cmds):
        pass




def crab_eater():
    pass




if __name__ == '__main__':
    rsc = RSCDealer()
    rsc.pros_page()
