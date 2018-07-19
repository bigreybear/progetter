from AbsDealer import AbsDealer as AD
from AbsDealer import POST, GET
import urllib2, urllib
import time
import json
import lxml.etree as etree
from loggetter import logger

class TRSDealer(AD):

    def __init__(self):
        AD.__init__(self)
        self.header['Accept-Encoding'] = "gzip, deflate, br"
        self.header['Accept-Language'] = "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,es;q=0.6,zh-TW;q=0.5"
        self.header['Content-Type'] = "application/json"

        # self.xpath_dic['href'] = '//div[@class="dir-member-name"]/a/@href'
        # self.xpath_dic['name'] = '//div[@class="dir-member-details"]/h3'
        # self.xpath_dic['year_selected'] = '//div[@class="member-info-section"]/div'
        # self.xpath_dic['citation'] = '//div[@class="member-details-text"]/p'
        # self.xpath_dic['previous_service'] = '//div[@class="member-info-section"]/ul/li'
        self.xpath_dic['bio'] = '//div[@class="expandableBio"]/p'

        # what is needed in return json
        self.target_list = [
            "ElectedYear",
            "FullNameWithHonours",
            "InstitutionName",
            "MemberType",
            "Position",
            "ScientificAreas",
            "Title"
        ]

        self.tmp_save_name = "trs.tmp"
        self.fin_save_name = "trs.bin"
        self.person_page_root = "https://royalsociety.org"
        self.current_page = ""
        self.valve = 50
        self.timeout = 5
        self.max_retry = 8
        self.interval_time = 3

    def router(self, cmd=None):
        _start_url = cmd['start_url']
        _offset = 0
        _payload = {
            "SearchType": "fellows",
            "Sort": "date",
            "StartIndex": 0,
            "PageSize": 12
        }
        ret = []
        while True:
            ret = self.json_handler(self.simple_post(_start_url, _payload))
            if len(ret) == 0:
                self.dealer_dump(False, True, True)
                logger.info("{} professor(s) finally dumped.".format(len(self.prf_list)))
                break
            _payload['StartIndex'] += len(ret)
            for prf in ret:
                _this_prf = {}
                for key in self.target_list:
                    _this_prf[key] = prf[key]
                _this_prf['bio'] = self.get_bio(prf['FellowProfileUrl'])
                self.prf_list.append(_this_prf)
                self.dict_printer(_this_prf)
                logger.info("{} professors had been recorded.".format(len(self.prf_list)))
            self.dealer_dump(False, True)

        return

    def get_bio(self, _p_url):
        _url = self.person_page_root + _p_url
        try:
            _content = etree.HTML(urllib.urlopen(_url).read())
        except UnicodeError:
            _url = urllib.quote(_url.encode('utf8'), ':/')
            _content = etree.HTML(urllib.urlopen(_url).read())
        if len(_content.xpath(self.xpath_dic['bio'])) >= 1:
            return _content.xpath(self.xpath_dic['bio'])[0].text
        else:
            return ""

    def json_handler(self, url_return):
        """
        :param url_return: Str from TRS url request open and read(), editable on json.
        :return: a list of target dictionary
        """
        _ret = []
        for p in json.loads(url_return.read())['Results']:
            _ret.append(p)
        return _ret

    def simple_post(self, _url, _data):
        """
        May not work in python3, and need no head for request.
        :param _url:
        :param _data:
        :return:
        """
        _tries = 0
        _params = urllib.urlencode(_data)
        while _tries < self.max_retry:
            try:
                _ret = urllib.urlopen(_url, _params)
                break
            except BaseException as e:
                if _tries < self.max_retry-1:
                    logger.info("Going to try {} time(s) at {}...".format(_tries, _url))
                    _tries += 1
                    time.sleep(self.interval_time)
                    continue
                else:
                    logger.info("Tried too many times at {}.".format(_url))
                    raise e
        return _ret

    def test_way(self):
        _payload = {
            "SearchType":"fellows",
            "Sort":"date",
            "StartIndex":0,
            "PageSize":12
        }
        _url = "https://royalsociety.org/api/Fellows/Search"
        # print self.get_bio("/people/andrew-king-13823")
        for i in self.json_handler(self.simple_post(_url, _payload)):
            self.dict_printer(i)
            print(self.get_bio(i['FellowProfileUrl']))



if __name__ == '__main__':
    trs = TRSDealer()
    # trs.test_way()
    trs.router({'start_url': "https://royalsociety.org/api/Fellows/Search"})
