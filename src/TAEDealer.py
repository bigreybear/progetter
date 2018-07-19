from AbsDealer import AbsDealer as AD
import lxml.etree as etree
import urllib, urllib2

class TAEDealer(AD):
    def __init__(self):
        AD.__init__(self)
        self.test_url = "https://www.ae-info.org/ae/Acad_Main/List_of_Members?type=searchresult&acad_section=" \
                        "&acad_elected=&acad_country=&acad_surname=&acad_former_member=null&pagenr=0#membersearch"

        self.header['Accept-Encoding'] = "gzip, deflate, br"
        self.header['Accept-Language'] = "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,es;q=0.6,zh-TW;q=0.5"
        self.header['Content-Type'] = "application/json"

        # self.xpath_dic['href'] = '//div[@class="dir-member-name"]/a/@href'
        # self.xpath_dic['name'] = '//div[@class="dir-member-details"]/h3'
        # self.xpath_dic['year_selected'] = '//div[@class="member-info-section"]/div'
        # self.xpath_dic['citation'] = '//div[@class="member-details-text"]/p'
        # self.xpath_dic['previous_service'] = '//div[@class="member-info-section"]/ul/li'
        # self.xpath_dic['bio'] = '//div[@class="expandableBio"]/p'

        self.xpath_dic['Present and Previous Positions'] = '//b[text()="Present and Previous Positions"]'
        self.xpath_dic['Fields of Scholarship'] = '//b[text()="Fields of Scholarship"]'
        self.xpath_dic['Honours and Awards'] = '//b[text()="Honours and Awards"]'

        self.xpath_dic['Email'] = '//td[text()="Email:"]/following-sibling::td'

        self.url_xpath = '//span[@class="name"]/b/a/@href'
        self.next_button = '//span[@class="last"]/../@href'

        # what is aimed to return by a list of str
        self.target_list = [
            "Honours and Awards",
            "Fields of Scholarship",
            "Present and Previous Positions"
        ]

        self.tmp_save_name = "tae.tmp"
        self.fin_save_name = "tae.bin"
        self.person_page_root = ""
        self.current_page = ""
        self.valve = 50
        self.timeout = 3
        self.max_retry = 8

    def collect_urls(self, _start_url=None):
        # _content = self.pros_page(_start_url)
        # _content = urllib2.urlopen(_start_url).read()
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
                # _content = self.pros_page(nxt_els[0])
                _content = self.simple_get(nxt_els[0], True)
        self.dealer_dump(True, False, True)

    def personal_info(self, _url):
        _content = etree.HTML(self.simple_get(_url, True))

        _this_prf = {}
        for target in self.target_list:
            if _content.xpath(self.xpath_dic[target])[0] is not None:
                _this_prf[target] = "; ".join([x.text[:-1] for x in _content.xpath(self.xpath_dic[target])[0].getnext().getchildren()])

        print(_content.xpath(self.xpath_dic['Email']).text)  # CANNOT FIND CORRECT ELEMENT
        self.dict_printer(_this_prf)

if __name__ == '__main__':
    tae = TAEDealer()
    # print(tae.simple_get(tae.test_url))
    # tae.collect_urls(tae.test_url)
    tae.personal_info("https://www.ae-info.org/ae/User/Zwirner_Fabio")
