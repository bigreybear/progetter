from loggetter import logger
import lxml.etree as etree
from src.AbsDealer import AbsDealer as AD
from src.AbsDealer import LAST_PAGE, ERROR_PAGE, NORMAL_PAGE


class AASDealer(AD):
    def __init__(self):
        AD.__init__(self)
        self.page_prefix = "https://www.science.org.au/fellowship/fellows?page=0"
        self.xpath_dic['href'] = '//div[@class="member-profile-text"]/h3/a/@href'
        self.xpath_dic['name'] = '//div[@class="member-details-wrap"]/h1'
        self.xpath_dic['year_selected'] = '//div[@class="member-sml-details hidden-sm hidden-xs"]/p'
        self.xpath_dic['citation'] = '//div[@class="member-details-text"]/p'

        self.tmp_save_name = "aas.tmp"
        self.fin_save_name = "aas.bin"
        self.person_page_root = "https://www.science.org.au/"
        self.current_page = ""
        self.valve = 50

    def one_page_pros(self, content_=None):
        # In AAS, you need pick all urls of personal page first.
        if content_ is None:
            content_ = self.pros_page(self.page_prefix)
        tree = etree.HTML(content_)
        hrefs = tree.xpath(self.xpath_dic['href'])
        for href in hrefs:
            self.url_list.append(href.encode('utf-8'))
        if len(hrefs) != 0:
            logger.info("Its a normal page and {} data accumulated.".format(len(self.url_list)))
            return NORMAL_PAGE
        else:
            return ERROR_PAGE

    def router(self, cmds=None):
        if cmds is None:
            cmds = {'phase': -1}
        if (cmds['phase'] == 1) or (cmds['phase'] == 0):
            # ***** ***** ***** ***** #
            # PHASE ONE: GET ALL URLS #
            # ***** ***** ***** ***** #
            url_page_count = 0
            self.current_page = "https://www.science.org.au/fellowship/fellows?page={}".format(url_page_count)
            while self.one_page_pros(self.pros_page(self.current_page)) == NORMAL_PAGE:
                url_page_count += 1
                self.current_page = "https://www.science.org.au/fellowship/fellows?page={}".format(url_page_count)
                self.dealer_dump(url_=True)
            self.dealer_dump(url_=True, fin_=True)

        if (cmds['phase'] == 2) or (cmds['phase'] == 0):

            # ***** ***** ***** ***** ***#
            # PHASE TWO: REBUILD AND GET #
            # ***** ***** ***** ***** ***#
            self.rebuild(url_=cmds['url_rebuild_src'])
            for purl in self.url_list:
                self.personal_page("{}/{}".format(self.person_page_root, purl))
                self.dealer_dump(prf_=True)
            self.dealer_dump(prf_=True, fin_=True)
        return 0

    def personal_page(self, url_=None):
        if url_ is None:
            content_ = self.pros_page(self.page_prefix)
        else:
            content_ = self.pros_page(url_)
        tree = etree.HTML(content_)
        data_ = {}
        for key, value in self.xpath_dic.items():
            if len(tree.xpath(value)) == 1:
                data_[key] = tree.xpath(value)[0].text.encode('utf-8')
            else:
                for e_part in tree.xpath(value):
                    if e_part.text is not None:
                        data_[key] = e_part.text.encode('utf-8')
        self.dict_printer(data_)
        self.prf_list.append(data_)
        logger.info("Accumulated {} data.".format(len(self.prf_list)))

    def to_debug(self):
        # target_url = "https://www.science.org.au/fellowship/fellows?page=22"
        # c_ = self.pros_page(target_url)
        # self.one_page_pros(target_url)
        # for i in self.url_list:
        #     print(i)
        self.personal_page("https://www.science.org.au///fellowship/fellows/professor-geordie-williamson")


if __name__ == '__main__':
    aas = AASDealer()
    aas.router({'phase': 2, 'url_rebuild_src': "url_aas_bak.tmp"})
    # aas.to_debug()