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

        self.xpath_dic['surname'] = '//div[@class="field field-name-field-surname field-type-text field-label-hidden"]' \
                                    '/div/div'
        self.xpath_dic['name'] = '//div[@class="field field-name-field-name field-type-text field-label-hidden"]' \
                                 '/div/div'
        self.xpath_dic['nationality'] = '//div[@class="field field-name-field-member-current-nationality ' \
                                        'field-type-taxonomy-term-reference field-label-above"]/div/div'
        self.xpath_dic['resident'] = '//div[@class="field field-name-field-shared-single-country field-type-taxonomy-' \
                                     'term-reference field-label-above"]/div/div'
        self.xpath_dic['institution'] = '//div[@class="field field-name-field-affiliation-institution ' \
                                        'field-type-text field-label-above"]/div/div'
        self.xpath_dic['elected'] = '//div[text()="Elected"]/../text()'
        self.xpath_dic['section'] = '//div[text()="Section:"]/../text()'

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
            _read = self.get_from_twas("https://twas.org/directory?page={}".format(url_i))
            tree = etree.HTML(_read)
            for target in tree.xpath(self.url_xpath):  # fill in the url_list
                if target not in self.non_target:
                    print(str(target))
                    self.url_list.append(str(target))
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
            _read = self.get_from_twas(self.person_page_root + url)
            self.prf_list.append(self.parse_personal_info(_read))
            self.dealer_dump(False, True)
        self.dealer_dump(False, True, True)

    def parse_personal_info(self, _content):
        tree = etree.HTML(_content)
        _this_prf = {}
        _debug = False
        for key, val in self.xpath_dic.items():
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
    twas = NobelDealer()
    # twas.rebuild("url_twas.bin")
    # twas.collect_personal_info()
    twas.pros_page("a")