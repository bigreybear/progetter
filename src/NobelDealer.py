from AbsDealer import AbsDealer as AD
import lxml.etree as etree
import time
from loggetter import logger
import sys
import StringIO
import gzip
# reload(sys)
# sys.setdefaultencoding("utf-8")


class NobelDealer(AD):
    def __init__(self):
        AD.__init__(self)
        self.test_url = ""

        self.header['Accept-Encoding'] = "gzip, deflate, br"
        self.header['Accept-Language'] = "q=0.9,en;q=0.8,ja;q=0.7,es;q=0.6,zh-TW;q=0.5"
        self.header['Content-Type'] = "application/json"

        self.xpath_dic['contents'] = '//div[@class="content"]/p'

        # self.url_xpath = '//div[@class="views-field views-field-title"]/span[@class="field-content"]/a/@href'
        self.url_xpath = '//p/a/@href'

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
            "https://www.nobelprize.org/prizes/lists/all-nobel-prizes-in-chemistry/",
            "https://www.nobelprize.org/prizes/lists/all-nobel-laureates-in-physiology-or-medicine/",
            "https://www.nobelprize.org/prizes/lists/all-nobel-prizes-in-literature/",
            "https://www.nobelprize.org/prizes/lists/all-nobel-peace-prizes/",
            "https://www.nobelprize.org/prizes/lists/all-prizes-in-economic-sciences/"
        ]

        self.tmp_save_name = "nobel.tmp"
        self.fin_save_name = "nobel.bin"
        self.person_page_root = "https://twas.org"
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
        _last_len = 0
        while _flag is True:
            time.sleep(1)
            _read = self.get_from_twas(_start_url)
            # _read = self.simple_get(_start_url, True)
            print _read
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
            if url.find("https://") == -1:
                _url = "https://" + url
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
        for key, val in self.xpath_dic.items():
            if key in ["contents"]:  # handle info in tag 'content'
                try:
                    _contents_p = tree.xpath(val)
                    for p in _contents_p:  # In nobels' page, content panel should get from a total p's
                        _pure_p = ' '.join(p.text.split())

                        if _pure_p.find("Born:") != -1:
                            _pure_p = _pure_p[6:]
                            _this_prf['born_date'] = _pure_p
                        elif _pure_p.find("Affiliation at the time of the award:") != -1:
                            _pure_p = _pure_p[len("Affiliation at the time of the award: "):]
                            _this_prf['affiliation_at_time'] = _pure_p
                        elif _pure_p.find("Prize motivation: ") != -1:
                            _pure_p = _pure_p[len("Prize motivation: ")+1:-1]
                            _this_prf['motivation'] = _pure_p
                        elif _pure_p.find("Prize share: ") != -1:
                            _pure_p = _pure_p[len("Prize share: "):]
                            _this_prf['share'] = _pure_p
                        else:
                            _this_prf['name'] = _pure_p
                            try:
                                #  HACK WAY TO GET YEAR
                                _prize_and_year = etree.HTML(_content).xpath('//div[@class="content"]/p/text()[contains(.,"Nobel")]')[0]
                                _prize_and_year = ' '.join(_prize_and_year.split())
                                _prize_and_year = _prize_and_year[len("The Nobel Prize in")+1:]
                                [_cate, _year] = _prize_and_year.split()
                                _this_prf['category'] = _cate
                                _this_prf['year'] = _year
                            except AttributeError:
                                continue

                except AttributeError:
                    _this_prf[key] = str(tree.xpath(val)[0])
                except BaseException as e:
                    if _debug:
                        logger.error("An error occurred at {} , {}".format(key, val))
                        print(e.message)
                        raise e
                    else:  # to continue rather than interrupt the flow
                        _this_prf[key] = ""
                        continue
            elif key in [""]:
                try:
                    _this_prf[key] = tree.xpath(val)[0].text
                except AttributeError:
                    _this_prf[key] = str(tree.xpath(val)[0])
                except BaseException as e:
                    if _debug:
                        logger.error("An error occurred at {} , {}".format(key, val))
                        print(e.message)
                        raise e
                    else:  # to continue rather than interrupt the flow
                        _this_prf[key] = ""
                        continue
        self.dict_printer(_this_prf)
        return _this_prf


if __name__ == '__main__':
    print("1700")
    nobel = NobelDealer()
    # twas.rebuild("url_twas.bin")
    # twas.collect_personal_info()
    # nobel.collect_urls(nobel.root_path[0])
    # for i in nobel.root_path:
    #     nobel.collect_urls(i)
    nobel.rebuild("url_nobel.bin")
    nobel.collect_personal_info()
    # nobel.parse_personal_info(nobel.get_from_twas("https://www.nobelprize.org/prizes/physics/2013/higgs/facts/"))