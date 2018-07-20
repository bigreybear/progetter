from AbsDealer import AbsDealer as AD
import lxml.etree as etree
import time
from loggetter import logger

class TAEDealer(AD):
    def __init__(self):
        AD.__init__(self)
        self.test_url = "https://www.ae-info.org/ae/Acad_Main/List_of_Members?type=searchresult&acad_section=" \
                        "&acad_elected=&acad_country=&acad_surname=&acad_former_member=null&pagenr=0#membersearch"

        self.header['Accept-Encoding'] = "gzip, deflate, br"
        self.header['Accept-Language'] = "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,es;q=0.6,zh-TW;q=0.5"
        self.header['Content-Type'] = "application/json"

        self.xpath_dic['Present and Previous Positions'] = '//b[text()="Present and Previous Positions"]'
        self.xpath_dic['Fields of Scholarship'] = '//b[text()="Fields of Scholarship"]'
        self.xpath_dic['Honours and Awards'] = '//b[text()="Honours and Awards"]'

        self.xpath_dic['Email'] = '//td[text()="Email:"]'
        self.xpath_dic['Membership type'] = '//td[text()="Membership type:"]'
        self.xpath_dic['Main Country of Residence'] = '//td[text()="Main Country of Residence:"]'
        self.xpath_dic['Section'] = '//td[text()="Section:"]'
        self.xpath_dic['Elected'] = '//td[text()="Elected:"]'
        self.xpath_dic['name'] = '//div[@id="pagecontent"]'

        self.url_xpath = '//span[@class="name"]/b/a/@href'
        self.next_button = '//span[@class="last"]/../@href'

        # what is aimed to return by a list of str
        self.target_list = [
            "Honours and Awards",
            "Fields of Scholarship",
            "Present and Previous Positions"
        ]

        self.target_list_2 = [
            "Email",
            "Membership type",
            "Main Country of Residence",
            "Elected"
        ]

        self.tmp_save_name = "tae.tmp"
        self.fin_save_name = "tae.bin"
        self.person_page_root = ""
        self.current_page = ""
        self.valve = 50
        self.timeout = 3
        self.max_retry = 8

    def collect_urls(self, _start_url=None):
        _content = self.simple_get(_start_url, True)
        while _content is not None:
            _tree = etree.HTML(_content)
            url_els = _tree.xpath(self.url_xpath)
            for el in url_els:
                self.url_list.append(el.encode('utf-8'))
            self.dealer_dump(True)
            print("Had dumped {} urls.".format(len(self.url_list)))
            if len(self.url_list) > 3785:
                break
            nxt_els = _tree.xpath(self.next_button)
            if len(nxt_els) > 1:
                _content = self.simple_get(nxt_els[0], True)
        self.dealer_dump(True, False, True)

    def personal_info(self, _url):
        _content = etree.HTML(self.simple_get(_url, True))

        _this_prf = {}
        for target in self.target_list:
            if len(_content.xpath(self.xpath_dic[target])) > 0 and \
                    _content.xpath(self.xpath_dic[target])[0] is not None:
                try:
                    _this_prf[target] = "; ".join([x.text[:-1] for x in _content.xpath(self.xpath_dic[target])[0].getnext().getchildren()])
                except TypeError as e:
                    _this_prf[target] = ""
                    logger.error("An error occurred.\n{}".format(e.message))

        for target in self.target_list_2:
            if len(_content.xpath(self.xpath_dic[target])) > 0 and \
                    _content.xpath(self.xpath_dic[target])[0] is not None:
                try:
                    _this_prf[target] = _content.xpath(self.xpath_dic[target])[0].getnext().text
                except TypeError as e:
                    _this_prf[target] = ""
                    logger.error("An error occurred.\n{}".format(e.message))

        _this_prf['name'] = _content.xpath(self.xpath_dic['name'])[0].getchildren()[0].text
        _this_prf['Section'] = _content.xpath(self.xpath_dic['Section'])[0].getnext().getchildren()[0].text

        self.dict_printer(_this_prf)
        return _this_prf

    def collect_personal_info(self):
        for url in self.url_list:
            time.sleep(0.5)
            self.prf_list.append(self.personal_info(url))
            self.dealer_dump(False, True, False)
            print("{}/{} professors had been dumped.".format(len(self.prf_list), len(self.url_list)))
        self.dealer_dump(False, True, True)

if __name__ == '__main__':
    tae = TAEDealer()
    # tae.collect_urls(tae.test_url)
    tae.rebuild("url_tae.bin")
    tae.url_list = list(set(tae.url_list))
    tae.collect_personal_info()
