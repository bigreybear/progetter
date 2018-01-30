from NASDealer import NASDealer as NASD
from selenium import webdriver
from bs4 import BeautifulSoup
import copy
import pickle


class NAEDealer(NASD, object):
    def __init__(self):
        NASD.__init__(self)
        self.mem_dir_page = "https://www.nae.edu/MembersSection/MemberDirectory.aspx"
        self.page_list = []  # url of target list
        self.page_prefix = "https://www.nae.edu"
        self.page_list_save_name = "nae_pl.tmp"
        pass

    def store_page_list(self, rewrite=True):
        if rewrite is True:
            with open("pagelist.tmp", "wb") as f:
                pickle.dump(self.page_list, f)
        else:
            with open("pagelist.tmp", "a") as f:
                pickle.dump(self.page_list, f)

    def one_professor(self, url):
        soup = self.get_soup(url)
        if soup is None:
            self.logger("Gotta Null soup, game stopped.")
            return 0
        res = {}

        for tag in soup.find_all("span", class_="name"):
            res['name'] = self.only_one_space(tag.contents[0])
        for tag in soup.find_all("span", class_="badge memberType member "):
            res['mem_type'] = self.only_one_space(tag.string)
        for tag in soup.find_all("span", class_="jobTitle border"):
            res['job_title'] = self.only_one_space(tag.string)
        for tag in soup.find_all("span", class_="organization border"):
            res['organization'] = self.only_one_space(tag.string)

        for tag in soup.find("ul", class_="ordList").contents:
            if tag.name == "li":
                for tags in tag.children:
                    if tags.name == "label":
                        _key = self.only_one_space(tags.string)
                    if tags.name == "span":
                        _ans = self.only_one_space(tags.string)
                res[_key] = _ans

        for __tag in soup.find_all("div", class_="content-box"):
            for e in __tag.children:
                if e.name == "div" and e['class'][0] == "description":
                    if e.string is not None:
                        res['citation'] = self.only_one_space(e.string)

        for k in res:
            print k, ' : ', res[k]
        print '-------------------'

        self.prf_list.append(copy.deepcopy(res))
        return


    def page_router(self, url, xpath="//*[@title=\"Next Page\"]"):
        """
        Manager for next page and so on. url is the member directory page.
        """
        browser = webdriver.Chrome()
        browser.get(url)
        try:
            elem = browser.find_element_by_xpath(xpath)
        except BaseException:
            self.logger("No more Next.")
            self.one_page(browser.page_source)
            self.save_obj(self.page_list, self.page_list_save_name)
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
                self.logger("No more Next.")
                print e.message
                browser.quit()
                self.save_obj(self.page_list, self.page_list_save_name)
                break
            finally:
                self.save_obj(self.page_list, self.page_list_save_name)
        self.save_obj(self.page_list, self.page_list_save_name)
        return

    def one_page(self, url):
        print 'hello'
        soup = BeautifulSoup(url, "lxml")
        for tag in soup.find_all("span", class_="name"):
            for tags in tag.children:
                print tags['href']
                self.page_list.append(tags['href'])
        self.store_page_list()
        print len(self.page_list)

    def crawl_from_url_list(self, filename, limit=-1):
        with open(filename, "rb") as f:
            url_list = pickle.load(f)
        print len(url_list)
        for i in range(len(url_list)):
            if limit > 0:
                limit -= 1
            if limit == 0:
                break
            self.one_professor(self.page_prefix + url_list[i])
            print i, '/', len(url_list)


if __name__ == '__main__':
    nae = NAEDealer()
    nae.logger("no")
    # soup = nae.get_soup("https://www.nae.edu/MembersSection/MemberDirectory/30595.aspx")
    # soup = nae.get_soup("https://www.nae.edu/MembersSection/MemberDirectory.aspx")
    # print soup.prettify()
    # nae.page_router(nae.mem_dir_page)
    # nae.one_professor("https://www.nae.edu/MembersSection/MemberDirectory/30265.aspx")
    nae.crawl_from_url_list("nae_pl.tmp", 20)