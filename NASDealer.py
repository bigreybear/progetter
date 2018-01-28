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
        self.timeout = 20
        self.request_prefix = "http://www.nasonline.org/member-directory/?q=&site=nas_members&requiredfields=("
        self.tmp_save_name = "lastget.bin"
        self.prf_list = []
        pass

    def temp_dump(self):
        with open(self.tmp_save_name, "wb") as f1:
            pickle.dump(self.prf_list, f1)

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

        self.prf_list.append(copy.deepcopy(res))
        return res

    def one_page(self, url):
        """
        To process a single page of professors, driven by a router determining when to exit.
        """
        soup = BeautifulSoup(url, "lxml")
        for tag in soup.find_all("a", ctype="c"):
            print tag['href']
            self.one_professor(tag['href'])
            time.sleep(self.interval_time)
        print len(self.prf_list)

    def page_router(self, url):
        browser = webdriver.Chrome()
        browser.get(url)
        try:
            elem = browser.find_element_by_xpath("//*[@ctype=\"nav.next\"]")
        except BaseException :
            self.logger("No more Next.")
        while elem is not None:
            self.logger("Once next page.", True)
            try:
                self.one_page(browser.page_source)
            except BaseException, e:
                self.logger("Now We Occur to a Exception, you can have the url when it broke down. Error message:")
                print e.message
                print browser.current_url
                return 0
            self.temp_dump()
            elem.click()
            try:
                elem = browser.find_element_by_xpath("//*[@ctype=\"nav.next\"]")
            except BaseException:
                self.logger("No more Next.")
                browser.quit()
                return
            finally:
                self.temp_dump()

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



    @staticmethod
    def only_one_space(src_str):
        return src_str.strip()



if __name__ == '__main__':
    nasd = NASDealer()
    # nasd.one_professor("http://www.nasonline.org/member-directory/members/56129.html")
    # nasd.one_professor("http://www.nasonline.org/member-directory/members/20041739.html")
    # nasd.one_professor("http://www.nasonline.org/member-directory/members/20041763.html")
    # nasd.page_router("http://www.nasonline.org/member-directory/?q=&site=nas_members&requiredfields=(member_electionyear:2009|member_electionyear:2008|member_electionyear:2007|member_electionyear:2006|member_electionyear:2005|member_electionyear:2004|member_electionyear:2003|member_electionyear:2002|member_electionyear:2001|member_electionyear:2000)")
    # nasd.temp_dump()
    # nasd.continue_from_point("http://www.nasonline.org/member-directory/?q=&site=nas_members&client=nas_members&proxystylesheet=nas_members&output=xml_no_dtd&filter=0&GSAhost=search.nationalacademies.org&unitsite=nas_members&unitname=NAS+Member+Directory&theme=gray&requestencoding=utf-8&s=&access=p&entqr=3&getfields=member_institution.member_section.member_secondary.member_fullname.member_lastname.member_firstname.member_date_of_birth.member_date_of_death.member_photopath&ie=UTF-8&ip=144.171.1.33&num=15&oe=UTF-8&requiredfields=(member_electionyear:2009%7Cmember_electionyear:2008%7Cmember_electionyear:2007%7Cmember_electionyear:2006%7Cmember_electionyear:2005%7Cmember_electionyear:2004%7Cmember_electionyear:2003%7Cmember_electionyear:2002%7Cmember_electionyear:2001%7Cmember_electionyear:2000)&sort=meta:metadata_sort&ud=1&ulang=&entqrm=0&wc=200&wc_mc=1&jsonp=jsonp1517075808140&start=720")
    nasd.page_router(nasd.get_start_by_year(2000, 2009))
    # with open("lastget.bin", "rb") as f:
    #     a2 = pickle.load(f)
    #     print a2