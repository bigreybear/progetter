from AbsDealer import AbsDealer as AD
import lxml.etree as etree
import time
from loggetter import logger
import sys
import StringIO
import gzip
# reload(sys)
# sys.setdefaultencoding("utf-8")


class TWASDealer(AD):
    def __init__(self):
        AD.__init__(self)
        self.test_url = ""

        self.header['Accept-Encoding'] = "gzip, deflate, br"
        self.header['Accept-Language'] = "q=0.9,en;q=0.8,ja;q=0.7,es;q=0.6,zh-TW;q=0.5"
        self.header['Content-Type'] = "application/json"

        self.xpath_dic['Email'] = ''

        self.url_xpath = '//div[@class="views-field views-field-title"]/span[@class="field-content"]/a/@href'
        self.next_button = ''

        # what is aimed to return by a list of str
        self.target_list = [

        ]

        self.target_list_2 = [
        ]

        self.non_target = [
            "/article/healing-plants-congo-0",
            "/article/more-scientists-decision-making-processes",
            "/article/vital-field-cooperation",
            "/article/crossing-two-oceans-science",
            "/article/victor-ramos-wins-twas-lenovo-prize"
        ]

        self.tmp_save_name = "twas.tmp"
        self.fin_save_name = "twas.bin"
        self.person_page_root = ""
        self.current_page = ""
        self.valve = 50
        self.timeout = 8
        self.max_retry = 8
        self.interval_time = 2

    def get_from_twas(self, _url):
        """
        Decode from the zipped data from TWAS.
        :param str _url:
        :return:
        """
        read = self.simple_get(_url, True)
        data = StringIO.StringIO(read)
        g_zipper = gzip.GzipFile(fileobj=data)
        return g_zipper.read()

    def collect_urls(self, _start_url="https://twas.org/directory"):
        url_i = 0
        _flag = True
        while _flag:
            time.sleep(1)
            _read = self.get_from_twas("https://twas.org/directory?page={}".format(url_i))
            tree = etree.HTML(_read)
            for target in tree.xpath(self.url_xpath):
                if target is None or len(target) == 0:
                    _flag = False
                    break
                if target not in self.non_target:
                    print(str(target))
                    self.url_list.append(str(target))
            self.dealer_dump(True, False, False)
            print("Has dumped {} urls.".format(len(self.url_list)))
            url_i += 1
        self.dealer_dump(True, False, True)


if __name__ == '__main__':
    print("1700")
    twas = TWASDealer()
    twas.collect_urls()
