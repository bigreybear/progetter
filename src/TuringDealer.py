from AbsDealer import AbsDealer as AD
import lxml.etree as etree
import time
from loggetter import logger
import sys
import StringIO
import gzip
reload(sys)
sys.setdefaultencoding("utf-8")


class TuringDealer(AD):
    def __init__(self):
        AD.__init__(self)
        self.test_url = ""

        self.header['Accept-Encoding'] = "gzip, deflate, br"
        self.header['Accept-Language'] = "q=0.9,en;q=0.8,ja;q=0.7,es;q=0.6,zh-TW;q=0.5"
        self.header['Content-Type'] = "application/json"

        self.xpath_dic['contents'] = '//div[@class="content"]/p'
        self.xpath_dic['description'] = '//div[@class="description"]/span/text()'
        self.xpath_dic['citation'] = '//div[@class="citation"]/p/text()'
        self.xpath_dic['name'] = '//h1[@class="country"]/a[1]/text()'
        self.xpath_dic['birth'] = '//h6/span[contains(text(),"BIRTH:")]/../following-sibling::p[1]/text()'
        self.xpath_dic['education'] = '//h6/span[contains(text(),"EDUCATION:")]/../following-sibling::p[1]/text()'
        self.xpath_dic['experience'] = '//h6/span[contains(text(),"EXPERIENCE:")]/../following-sibling::p[1]/text()'
        self.xpath_dic['honorAndAward'] = '//h6/span[contains(text(),"HONORS AND AWARDS")]/../following-sibling::p[1]/text()'


        # self.url_xpath = '//div[@class="views-field views-field-title"]/span[@class="field-content"]/a/@href'
        self.url_xpath = '//div[@class="inner"]/ul/li/a/@href'

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

        self.root_path = [
            "https://www.nobelprize.org/prizes/lists/all-nobel-prizes-in-physics/",
        ]

        self.tmp_save_name = "turing.tmp"
        self.fin_save_name = "turing.bin"
        self.person_page_root = "https://twas.org"
        self.current_page = ""
        self.valve = 30
        self.timeout = 8
        self.max_retry = 8
        self.interval_time = 5

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
        _last_len = 0
        while _flag is True:
            time.sleep(1)
            _read = self.get_from_twas(_start_url)
            # _read = self.simple_get(_start_url, True)
            # print _read
            tree = etree.HTML(_read)
            for target in tree.xpath(self.url_xpath):  # fill in the url_list
                if target not in self.non_target:  # exclude useless urls
                    print(str(target))
                    self.url_list.append(str(target))
            _flag = False  # exit immediately
            if len(self.url_list) - _last_len > 0:
                _last_len = len(self.url_list)
            else:  # For there could be some other urls in content, we don't judge just on length.
                _flag = False
            self.dealer_dump(True, False, False)
            print("Has dumped {} urls.".format(len(self.url_list)))
            url_i += 1
        self.dealer_dump(True, False, True)

    def collect_personal_info(self):
        for url in self.url_list:
            _url = None
            time.sleep(0.5)
            if url.find("https://amturing.acm.org/") == -1:
                _url = "https://amturing.acm.org/" + url
            if _url is None:
                _url = url
            _read = self.get_from_twas(_url)
            self.prf_list.append(self.parse_personal_info(_read))
            self.dealer_dump(False, True)
        self.dealer_dump(False, True, True)

    def parse_personal_info(self, _content):
        tree = etree.HTML(_content)
        _this_prf = {}
        _debug = False

        #
        #  CORE PARSER
        #
        for key, val in self.xpath_dic.items():
            _content = tree.xpath(val)
            if type(_content) is list and len(_content) != 0:
                _this_prf[key] = str(_content[0])
            elif type(_content) is not list:
                _this_prf[key] = str(_content)

        self.dict_printer(_this_prf)
        return _this_prf


if __name__ == '__main__':
    print("1700")
    nobel = TuringDealer()
    # twas.rebuild("url_twas.bin")
    # twas.collect_personal_info()
    # nobel.collect_urls("https://amturing.acm.org/byyear.cfm")
    # for i in nobel.root_path:
    #     nobel.collect_urls(i)
    nobel.rebuild("url_turing.bin")
    nobel.collect_personal_info()
    # nobel.parse_personal_info(nobel.get_from_twas("https://amturing.acm.org/award_winners/sifakis_1701095.cfm"))
    # nobel.simple_get("https://www.nobelprize.org/prizes/medicine/2018/honjo/facts/")