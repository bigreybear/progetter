from AbsDealer import AbsDealer as AD
import lxml.etree as etree
import time
from loggetter import logger
import sys
import StringIO
import gzip
import json
import requests
import  re
reload(sys)
sys.setdefaultencoding("utf-8")


class Pulitzer(AD):
    def __init__(self):
        AD.__init__(self)
        self.test_url = ""

        self.header['Accept-Encoding'] = "gzip, deflate, br"
        self.header['Accept-Language'] = "q=0.9,en;q=0.8,ja;q=0.7,es;q=0.6,zh-TW;q=0.5"
        self.header['Content-Type'] = "application/json"
        self.header['Referer'] = "https://www.pulitzer.org/prize-winners-by-year"

        self.xpath_dic['contents'] = '//div[@class="content"]/p'
        self.xpath_dic['description'] = '//div[@class="description"]/span/text()'
        self.xpath_dic['citation'] = '//div[@class="citation"]/p/text()'
        self.xpath_dic['name'] = '//h1[@class="country"]/a[1]/text()'
        self.xpath_dic['birth'] = '//h6/span[contains(text(),"BIRTH:")]/../following-sibling::p[1]/text()'
        self.xpath_dic['education'] = '//h6/span[contains(text(),"EDUCATION:")]/../following-sibling::p[1]/text()'
        self.xpath_dic['experience'] = '//h6/span[contains(text(),"EXPERIENCE:")]/../following-sibling::p[1]/text()'
        self.xpath_dic['honorAndAward'] = '//h6/span[contains(text(),"HONORS AND AWARDS")]/../following-sibling::p[1]/text()'


        # self.url_xpath = '//div[@class="views-field views-field-title"]/span[@class="field-content"]/a/@href'
        self.url_xpath = '//a[@ng-bind="::category.name"]/text()'

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

        self.tmp_save_name = "pulitzer.tmp"
        self.fin_save_name = "pulitzer.bin"
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
        _json = []

        time.sleep(1)
        # _read = self.get_from_twas(_start_url)
        for tries in range(30):
            try:
                _read = self.simple_get(_start_url, True)
                _json = json.loads(str(_read))
                break
            except BaseException as e:
                if tries > 9:
                    self.url_list.append({'failed_year_page': _start_url})
                    return
                logger.error("Exception: {}, retry {} at {} times.".format(e, _start_url, tries))
                continue
        if len(_json) <= 0:
            self.url_list.append({'failed_year_page': _start_url})
            return
        for item in _json:
            _this_url = {}
            if 'field_abbr_citation' in item and 'und' in item['field_abbr_citation']:
                _this_url['citation'] = item['field_abbr_citation']['und'][0]['safe_value']
            if 'field_category' in item and 'und' in item['field_category']:
                _this_url['category'] = item['field_category']['und'][0]['tid']
            _this_url['url'] = item['path_alias']
            _this_url['title'] = item['title']
            if 'field_publisher' in item and 'und' in item['field_publisher']:
                _this_url['publisher'] = item['field_publisher']
            _this_url['year'] = item['field_year']['und'][0]['tid']
            _this_url['original_content'] = json.dumps(item)
            self.dict_printer(_this_url)
            self.url_list.append(_this_url)
        # print _read

        # self.dealer_dump(True, False, True)

    def collect_personal_info(self):
        all_cnt = len(self.url_list)
        cnt = 0
        for url_obj in self.url_list:
            cnt += 1
            _url = None
            time.sleep(0.5)
            _url = "https://www.pulitzer.org/cache/api/1/node/{}/raw.json".format(json.loads(url_obj['original_content'])['nid'])
            for tries in range(30):
                try:
                    _read = self.simple_get(_url, True)
                    _json = json.loads(str(_read))
                    break
                except BaseException as e:
                    if tries > 29:
                        self.url_list.append({'failed_year_page': _url})
                        return
                    logger.error("Exception: {}, retry {} at {} times.".format(e, _url, tries))
                    continue
            self.prf_list.append(_json)
            self.dealer_dump(False, True)
            self.dict_printer(_json)
            print("Now {} / {}".format(cnt, all_cnt))
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

    def parse_json_obj(self, obj, fore_path=""):
        flat_obj = {}
        if type(obj) is dict:
            for item, value in obj.items():
                if item.find("field_list_of_works") != -1 or \
                        item.find("field_article_collection") !=-1 or \
                        item.find("field_regular_image_slider") != -1 or \
                        item.find("field_bio_photo") != -1 or \
                        item.find("field_associated_person") != -1 or \
                        item.find("filename") != -1 or \
                        item.find("filesize") != -1:
                    continue
                _parse_res = self.parse_json_obj(value, fore_path+"/"+item)
                for k, v in _parse_res.items():
                    flat_obj[k] = str(v)
        elif type(obj) is list:
            for index in range(len(obj)):
                if index >= 1:
                    continue
                _parse_res = self.parse_json_obj(obj[index], fore_path+"/"+str(index))
                for k, v in _parse_res.items():
                    flat_obj[k] = str(v)
        else:
            if str(obj) == "\n":
                obj = obj[:-1]
            c = re.sub('<[^<]+?>', '', str(obj)).replace('\n', '').strip()
            flat_obj[fore_path+"__val"] = c
        # target to return a 1-level obj
        return flat_obj


if __name__ == '__main__':
    print("1700")
    nobel = Pulitzer()
    # twas.rebuild("url_twas.bin")
    # twas.collect_personal_info()
    # nobel.collect_urls("https://www.pulitzer.org/prize-winners-by-year/2018")
    # for i in nobel.root_path:
    # i = 203
    # while i >= 104:
    #     url = "https://www.pulitzer.org/cache/api/1/winners/year/{}/raw.json".format(i)
    #     print("Now collecting pulitzer at year {}.".format(2120-i))
    #     nobel.collect_urls(url)
    #     i -= 1
    # nobel.collect_urls("https://www.pulitzer.org/cache/api/1/winners/year/601/raw.json")
    # nobel.collect_urls("https://www.pulitzer.org/cache/api/1/winners/year/613/raw.json")
    # nobel.dealer_dump(True, False, True)
    # print _ret
    #
    # _json = json.loads(str(_ret))
    # for i in _json:
    #     print i['type'], i['title'], i['field_year']['und'][0]['tid']
    #     nobel.collect_urls(i)
    # nobel.rebuild("url_turing.bin")
    # nobel.collect_personal_info()
    # nobel.parse_personal_info(nobel.get_from_twas("https://amturing.acm.org/award_winners/sifakis_1701095.cfm"))
    # nobel.simple_get("https://www.nobelprize.org/prizes/medicine/2018/honjo/facts/")

    nobel.rebuild(None, "prf_pulitzer_CompSource.bin")
    coord = {}
    for _i in range(len(nobel.prf_list)):
        nobel.prf_list[_i] = nobel.parse_json_obj(nobel.prf_list[_i], "")
        for attr in nobel.prf_list[_i]:
            if attr not in coord:
                coord[attr] = 0
            coord[attr] += 1
        nobel.dict_printer(nobel.prf_list[_i])


    print len(coord)
    nobel.dict_printer(coord)
    nobel.dealer_dump(False, True, True)


    # nobel.collect_personal_info()
    # s = requests.session()
    # url = "https://www.pulitzer.org/prize-winners-by-year/2017"
    # resp1 = s.get(url)
    # headers = {'Referer': 'https://www.pulitzer.org/prize-winners-by-year/2017'}
    # api = "https://www.pulitzer.org/cache/api/1/winners/year/166/raw.json"
    # data = s.get(api, headers=headers)
    # print data