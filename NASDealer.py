import urllib2
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from bs4 import NavigableString

class NASDealer:
    def __init__(self):
        self.header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/64.0.3282.119 Safari/537.36"}
        self.is_debug = True
        self.page_prefix = "http://www.nasonline.org/member-directory/"
        self.prf_list = []
        pass

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
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print e.code
        except urllib2.URLError, e:
            print e.reason
        soup = BeautifulSoup(response.read(), "lxml")
        return soup

    def one_professor(self, url):
        """
        Give it a url and it'll return a dictionary which tells all info you want.
        """
        soup = self.get_soup(url)
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
        return res

    def one_page(self, url):
        """
        To process a single page of professors, driven by a router determining when to exit.
        """
        soup = BeautifulSoup(url, "lxml")
        for tag in soup.find_all("a", ctype="c"):
            print tag['href']
            self.prf_list.append(self.one_professor(tag['href']))
            time.sleep(2)
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
            self.one_page(browser.page_source)
            elem.click()
            try:
                elem = browser.find_element_by_xpath("//*[@ctype=\"nav.next\"]")
            except BaseException:
                self.logger("No more Next.")
                browser.quit()
                return


    @staticmethod
    def only_one_space(src_str):
        return src_str.strip()



if __name__ == '__main__':
    nasd = NASDealer()
    # nasd.one_professor("http://www.nasonline.org/member-directory/members/20041821.html")
    # nasd.one_professor("http://www.nasonline.org/member-directory/members/20041739.html")
    # nasd.one_professor("http://www.nasonline.org/member-directory/members/20041763.html")
    nasd.page_router("http://www.nasonline.org/member-directory/?q=&site=nas_members&requiredfields=(member_electionyear:2017)")