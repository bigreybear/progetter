import urllib2
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from bs4 import NavigableString
import pickle
import copy


class NASDealer:
    def __init__(self):
        self.header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/64.0.3282.119 Safari/537.36"}
        self.is_debug = True
        self.page_prefix = "http://www.nasonline.org/member-directory/"
        self.interval_time = 5
        self.timeout = 40
        self.request_prefix = "http://www.nasonline.org/member-directory/?q=&site=nas_members&requiredfields=("
        self.tmp_save_name = "lastget.bin"
        self.prf_list = []
        self.nas_page_list = []
        self.nas_page_list_save_name = "nas_pl.tmp"
        self.url_list = None
        pass

    def temp_dump(self):
        with open(self.tmp_save_name, "wb") as f1:
            pickle.dump(self.prf_list, f1)

    def save_obj(self, obj, filename):
        with open(filename, "wb") as f:
            pickle.dump(obj, f)

    def logger(self, words, debug=False):
        if debug is True:
            # only in debug mode this line shoud be printed
            if self.is_debug is False:
                return
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
        print words

    def get_soup(self, url):
        req = urllib2.Request(url, headers=self.header)
        try:
            response = urllib2.urlopen(req, timeout=self.timeout)
        except urllib2.HTTPError, e:
            print e.code
        except urllib2.URLError, e:
            self.logger("We got a ERROR named: " + e.reason + ", and now we'll take another chance.")
            try:
                response = urllib2.urlopen(req, timeout=self.timeout + 10)
            except urllib2.URLError, e:
                self.logger("We tried twice, but failed neither. Reason: " + e.reason)
                return
        soup = BeautifulSoup(response.read(), "lxml")
        return soup

    def one_professor(self, url):
        """
        Give it a url and it'll return a dictionary which tells all info you want.
        """
        soup = self.get_soup(url)
        if soup is None:
            self.logger("Gotta Null soup, game stopped.")
            return 0
        res = {}

        # professor's name
        for tag in soup.find_all("div", id="contact_info"):
            for s_tag in tag.descendants:
                if s_tag.name == "h2":
                    _name = self.only_one_space(s_tag.string)
                    self.logger("Start to process Prof. " + _name)
                    res['name'] = _name
                if s_tag.name == 'h3':
                    _school = self.only_one_space(s_tag.string)
                    self.logger(_school, True)
                    res['school'] = _school
        # info about election
        for tag in soup.find_all("span", style="font-weight:bold;"):
            # print(tag.string)
            if tag.string == "Election Year:":
                _elec_year = self.only_one_space(tag.next_sibling.string)
                self.logger(_elec_year, True)
                res['elec_year'] = _elec_year
            if tag.string == "Primary Section:":
                _pri_sec = self.only_one_space(tag.next_sibling.string)
                self.logger(_pri_sec, True)
                res['prim_sec'] = _pri_sec
            if tag.string == "Membership Type:":
                _mem_type = self.only_one_space(tag.next_sibling.string)
                self.logger(_mem_type, True)
                res['mem_type'] = _mem_type
            if tag.string == "Secondary Section:":
                _sec_sec = self.only_one_space(tag.next_sibling.string)
                self.logger(_sec_sec, True)
                res['sec_sec'] = _sec_sec

        # sketch and interest
        for tag in soup.find_all("div", id="biosketch"):
            # to handle if text is cut to multiple tags
            _complete_text = []
            _bio = ""
            for s_tag in tag.descendants:
                if s_tag.name == "p":
                    if s_tag.string is None:
                        # to handle if text is cut to multiple paragraph, but in one tag <p>
                        _tmp = []
                        for content in s_tag.contents:
                            if type(content) is NavigableString:
                                _tmp.append(content)
                        _bio = "".join(_tmp)
                    else:
                        _bio = self.only_one_space(s_tag.string)
                _complete_text.append(_bio)
            res['biosketch'] = "".join(_complete_text)
            self.logger(res['biosketch'], True)
        for tag in soup.find_all("div", id="research_intrests"):
            _complete_text = []
            _interest = ""
            for s_tag in tag.descendants:
                if s_tag.name == "p":
                    if s_tag.string is None:
                        _tmp = []
                        for content in s_tag.contents:
                            if type(content) is NavigableString:
                                _tmp.append(content)
                        _interest = "".join(_tmp)
                    else:
                        _interest = self.only_one_space(s_tag.string)
                _complete_text.append(_interest)
            res['interest'] = "".join(_complete_text)
            self.logger(res['interest'], True)

        for k in res:
            print k, ': ', res[k]
        print '--------------------'

        self.prf_list.append(copy.deepcopy(res))
        return res

    def one_page(self, url):
        """
        To process a single page of professors, driven by a router determining when to exit.
        """
        soup = BeautifulSoup(url, "lxml")
        for tag in soup.find_all("a", ctype="c"):
            print tag['href']
            self.nas_page_list.append(tag['href'])
            # self.one_professor(tag['href'])
            # time.sleep(self.interval_time)
        # self.save_obj(self.nas_page_list, "nas_pl.tmp")
        print len(self.nas_page_list)

    def page_router(self, url, xpath="//*[@ctype=\"nav.next\"]"):
        browser = webdriver.Chrome()
        browser.get(url)
        try:
            elem = browser.find_element_by_xpath(xpath)
        except BaseException :
            self.logger("No more Next.")
            self.one_page(browser.page_source)
            self.save_obj(self.nas_page_list, self.nas_page_list_save_name)
            browser.quit()
            return
        while elem is not None:
            self.logger("Once next page.", True)
            try:
                self.one_page(browser.page_source)
            except BaseException, e:
                self.logger("Now We Occur to a Exception, you can have the url when it broke down. Error message:")
                print e.message
                print e.args
                print browser.current_url
                return 0
            self.temp_dump()
            elem.click()
            try:
                elem = browser.find_element_by_xpath(xpath)
            except BaseException, e:
                self.one_page(browser.page_source)
                self.logger("No more Next.")
                print e.message
                browser.quit()
                self.save_obj(self.nas_page_list, self.nas_page_list_save_name)
                break
            finally:
                self.save_obj(self.nas_page_list, self.nas_page_list_save_name)

        return

    def continue_from_point(self, url):
        with open(self.tmp_save_name, "rb") as f:
            _temp_list = pickle.load(f)
            self.prf_list = copy.deepcopy(_temp_list)
        self.page_router(url)

    def get_start_by_year(self, start, end):
        _url = self.request_prefix
        if start == end:
            _url += "member_electionyear:" + str(start) +")"
        elif start > end:
            self.get_start_by_year(end, start)
        else:
            _i = start
            while _i != end:
                _url += "member_electionyear:" + str(_i) + "|"
                _i += 1
            _url += "member_electionyear:" + str(_i) + ")"
        self.logger("url: " + _url, True)
        return _url

    def merge_list(self):
        with open("./nas_pl/nas_1958-.tmp", "rb") as f:
            a1 = pickle.load(f)
            print len(a1)
        with open("./nas_pl/nas_1958-1987.tmp", "rb") as f:
            a1 += pickle.load(f)
            print len(a1)
        with open("./nas_pl/nas_1988-1997.tmp", "rb") as f:
            a1 += pickle.load(f)
            print len(a1)
        with open("./nas_pl/nas_1998-2007.tmp", "rb") as f:
            a1 += pickle.load(f)
            print len(a1)
        with open("./nas_pl/nas_2007-2018.tmp", "rb") as f:
            a1 += pickle.load(f)
            print len(a1)
        self.url_list = copy.deepcopy(a1)


    @staticmethod
    def only_one_space(src_str):
        return src_str.strip()



if __name__ == '__main__':
    nasd = NASDealer()
    # nasd.one_professor("http://www.nasonline.org/member-directory/members/47100.html")
    # nasd.one_professor("http://www.nasonline.org/member-directory/members/58107.html")
    # nasd.one_professor("http://www.nasonline.org/member-directory/members/20041763.html")
    # nasd.page_router("http://www.nasonline.org/member-directory/?q=&site=nas_members&requiredfields=(member_electionyear:2009|member_electionyear:2008|member_electionyear:2007|member_electionyear:2006|member_electionyear:2005|member_electionyear:2004|member_electionyear:2003|member_electionyear:2002|member_electionyear:2001|member_electionyear:2000)")
    # nasd.temp_dump()
    # nasd.continue_from_point("http://www.nasonline.org/member-directory/?q=&site=nas_members&client=nas_members&proxystylesheet=nas_members&output=xml_no_dtd&filter=0&GSAhost=search.nationalacademies.org&unitsite=nas_members&unitname=NAS+Member+Directory&theme=gray&requestencoding=utf-8&s=&getfields=member_institution.member_section.member_secondary.member_fullname.member_lastname.member_firstname.member_date_of_birth.member_date_of_death.member_photopath&num=15&requiredfields=(member_electionyear:1968%7Cmember_electionyear:1969%7Cmember_electionyear:1970%7Cmember_electionyear:1971%7Cmember_electionyear:1972%7Cmember_electionyear:1973%7Cmember_electionyear:1974%7Cmember_electionyear:1975%7Cmember_electionyear:1976%7Cmember_electionyear:1977%7Cmember_electionyear:1978%7Cmember_electionyear:1979%7Cmember_electionyear:1980%7Cmember_electionyear:1981%7Cmember_electionyear:1982%7Cmember_electionyear:1983%7Cmember_electionyear:1984%7Cmember_electionyear:1985%7Cmember_electionyear:1986%7Cmember_electionyear:1987)&sort=meta:metadata_sort&jsonp=jsonp1517312357704&oe=UTF-8&ie=UTF-8&ulang=&ip=144.171.1.33&access=p&entqr=3&entqrm=0&wc=200&wc_mc=1&ud=1&start=15")
    # nasd.page_router(nasd.get_start_by_year(2008, 2018))
    # nasd.save_obj(nasd.nas_page_list, nasd.nas_page_list_save_name)
    # with open("lastget.bin", "rb") as f:
    #     a2 = pickle.load(f)
    #     print a2
    nasd.merge_list()
    nasd.save_obj(nasd.url_list, "nas_pl.tmp")
    print len(nasd.url_list)