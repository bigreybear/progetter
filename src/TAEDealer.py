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

        self.url_xpath = '//span[@class="name"]/b/a/@href'
        self.next_button = '//span[@class="last"]/../@href'

        # # what is needed in return json
        # self.target_list = [
        #     "ElectedYear",
        #     "FullNameWithHonours",
        #     "InstitutionName",
        #     "MemberType",
        #     "Position",
        #     "ScientificAreas",
        #     "Title"
        # ]

        self.tmp_save_name = "tae.tmp"
        self.fin_save_name = "tae.bin"
        self.person_page_root = ""
        self.current_page = ""
        self.valve = 50
        self.timeout = 5
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



if __name__ == '__main__':
    tae = TAEDealer()
    tae.collect_urls(tae.test_url)
