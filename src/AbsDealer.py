import pickle
import os
from loggetter import logger
import urllib2
import urllib
import time

LAST_PAGE = -1
ERROR_PAGE = 0
NORMAL_PAGE = 1
POST = 1
GET = 0


class AbsDealer:
    def __init__(self):
        self.header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/64.0.3282.119 Safari/537.36"}
        self.is_debug = False
        # time between two request, not to be banned.
        self.interval_time = 2
        # maximum retry in a urlopen
        self.max_retry = 10
        self.timeout = 40
        self.request_prefix = ""

        self.prj_loc = "F:\PyProject\ProfGetter\\"
        # periodically, pickle dump the PRF_LIST or URL_LIST to middle/TMP_SAVE_NAME to save the process,
        # and the finished file name.
        self.tmp_save_name = ""
        self.fin_save_name = ""
        # valve decide how many entries will at least make a dump
        # dump_count records how many times it had dumped and to judge whether should dump
        self.valve = 0
        self.dump_count = {'url': 0, 'prf': 0}
        # page_prefix is the main crawl page root, crawler start here.
        self.page_prefix = ""
        # crawl counter.
        self.cnt = 0
        # professor data list, each of which is a dictionary.
        self.prf_list = []
        # professor personal page url list.
        self.url_list = []
        # specify how to pick data from lowest page
        self.xpath_dic = {}
        pass

    def pros_page(self, url=None, method_=GET, data_=None):
        """
        To get the content of a page, without deal it with bs4, without construct url itself.
        :param url: The fetch url.
        :param method_: Specify GET or POST method to retrieve data.
        :param data_: A dictionary contains data POST method needs.
        :return: page source of the url.
        """
        if url is None:
            url = self.page_prefix
        _content = None
        if method_ == POST:
            if data_ is None:
                logger.error("No data for POST request for {}.".format(url))
            else:
                data_ = urllib.urlencode(data_).encode('utf-8')
                _req = urllib2.Request(url, headers=self.header, data=data_)
                logger.info("Formed a POST request for url: {}".format(_req.data))
        else:
            _req = urllib2.Request(url, headers=self.header)
            logger.info("Formed a GET request for url: {}".format(_req))
        for tries in range(self.max_retry):
            try:
                time.sleep(self.interval_time)
                _content = urllib2.urlopen(_req, timeout=self.timeout * 1000, data=data_)
                break
            except urllib2.URLError:
                if tries < (self.max_retry - 1):
                    continue
                else:
                    logger.error("Tried {} times to connect url:{}, but failed.".format(self.max_retry, url))
                    raise urllib2.URLError
        _ret = _content.read()
        _content.close()
        logger.debug("Processing url: {}".format(url))
        return _ret

    def personal_page(self, url=None):
        """
        If this website have every professor a personal page, we will get info from here.
        :param url: professor's personal page url.
        :return:
        """

    def router(self, cmd=None):
        """
        Core method to Control how to get every professor's personal page.
        Need to construct url for every @method:pros_page.
        :param cmd: K-V commands to control the router, according to different website.
        :return:
        """

    def one_page_pros(self, content_=None):
        """
        To deal a page of pros, get every professor's personal page url and save it (if necessary),
        or rarely, pick the data of every professor directly and save it and so on.
        :param content_: urllib2 read output of the pros_page.
        :return:
        """

    def periodical_dump_prf(self):
        """
        Periodically dump the PRF_LIST into a middle file named by TMP_SAVE_NAME.
        :return:
        """

    def periodical_dump_url(self):
        """
        Periodically dump the URL_LIST into a middle file named by TMP_SAVE_NAME.
        :return:
        """

    def rebuild(self, url_=None, prf_=None):
        """
        To rebuild the url_list or prf_list from a source file.
        :param url_: file path of url_list tmp file relative to project root path.
        :param prf_: file path of prf_list ...
        :return:
        """
        if (url_ is None) and (prf_ is None):
            logger.info("Rebuild source is not specified.")
            return -1
        ori_path_ = os.getcwd()
        if url_ is not None:
            os.chdir(self.prj_loc)
            with open("{}/middle/{}".format(self.prj_loc, url_), "r") as f:
                self.url_list = pickle.load(f)
            logger.info("{} reload to url_list, length: {}.".format(url_, len(self.url_list)))
            os.chdir(ori_path_)
        if prf_ is not None:
            os.chdir(self.prj_loc)
            with open("{}/middle/{}".format(self.prj_loc, prf_), "r") as f:
                self.prf_list = pickle.load(f)
            logger.info("{} reload to prf_list, length: {}.".format(prf_, len(self.prf_list)))
            os.chdir(ori_path_)
        logger.info("Rebuild completed.")
        return 0

    def dealer_dump(self, url_=False, prf_=False, fin_=False):
        """
        Decide what dump_count is.
        Periodically or finally dump the prf_list or url_list to the corresponding place.
        :param url_: if to dump url_list
        :param prf_: if to dump prf_list
        :param fin_: whether the last dump, works for both url_ and prf_
        :return:
        """
        ori_path_ = os.getcwd()
        ready_prf_ = False
        ready_url_ = False

        if not fin_:
            os.chdir("{}/middle/".format(self.prj_loc))
            file_name_ = self.tmp_save_name
            if ((len(self.prf_list) / self.valve) > self.dump_count['prf']) and prf_:
                self.dump_count['prf'] = len(self.prf_list) / self.valve
                ready_prf_ = True
                logger.info("Able to periodically dump PRF_LIST at {} times.".format(self.dump_count['prf']))
            if ((len(self.url_list) / self.valve) > self.dump_count['url']) and url_:
                self.dump_count['url'] = len(self.url_list) / self.valve
                ready_url_ = True
                logger.info("Able to periodically dump URL_LIST at {} times.".format(self.dump_count['url']))
        else:
            os.chdir("{}/raw/".format(self.prj_loc))
            file_name_ = self.fin_save_name
            ready_prf_ = True
            ready_url_ = True

        if url_ and ready_url_:
            with open("url_{}".format(file_name_), "wb") as f:
                pickle.dump(self.url_list, f)
            logger.info("Dump {} data into url_{}.".format(len(self.url_list), file_name_))
        if prf_ and ready_prf_:
            with open("prf_{}".format(file_name_), "wb") as f:
                pickle.dump(self.prf_list, f)
            logger.info("Dump {} data into prf_{}".format(len(self.prf_list), file_name_))
        if (not url_) and (not prf_):
            logger.error("Not specified to dump url or professor data.")
            os.chdir(ori_path_)
            return -1
        os.chdir(ori_path_)
        return 0

    @staticmethod
    def dict_printer(dict_):
        for key, value in sorted(dict_.items()):
            print key, ": ", value
        print("-----------------")
