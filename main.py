import datetime
import time

import requests
from bs4 import BeautifulSoup

from helper.settings import *
from helper.get_cookie import get_headers
# from helper.api import Website, get_last_zid
from helper.captcha import Captcha
from helper.country_code import country_code_list
from helper.proxies.proxies_crawler import ProxiesManagement
from helper.timeout import timeout
from helper.thread_pool import ThreadPool


class Crawler:
    def __init__(self, zid, headers, proxy, crawler_num):
        self.zid = zid
        self.url = "%s%s" % (ZONE_H_MIRROR, zid)
        self.proxy = proxy
        self.headers = headers
        self.soup = None
        self.address = None
        self.hacked_time = None
        self.proof = None
        self.notified_by = None
        self.system = None
        self.web_server = None
        self.ip_address = None
        self.country = None
        self.source = 'http://zone-h.org'
        self.crawler_num = crawler_num

    def parse(self):
        try:
            print("Parsing %s | Proxy %s" % (self.url, self.proxy))
            r = requests.get(self.url, headers=self.headers, proxies=self.proxy, timeout=10)
            if len(r.cookies) != 0:
                for cookie in r.cookies:
                    self.headers['Cookie'] += '; %s=%s' % (cookie.name, cookie.value)

            if CAPTCHA_SIGN in r.text:
                # return False
                try:
                    mediator = self.bypass_captcha()
                    if mediator:
                        r = mediator
                    else:
                        return False
                except Exception as e:
                    return False

            if r.status_code == 404:
                return True

            if EMPTY_SIGN in r.text:
                return True

            if BLOCK_SIGN in r.text \
                    or 'The following error was encountered while trying to retrieve the URL:' in r.text:
                return False

            if EXPIRED_COOKIE_SIGN in r.text:
                self.headers = get_headers(self.proxy)
                r = requests.get(self.url, headers=self.headers, proxies=self.proxy, timeout=10)

            if self.work(r):
                return True
            else:
                return False

        except:
            return False

    @timeout(60)
    def bypass_captcha(self):
        print("We have met a captcha at %s | Proxy %s" % (self.url, self.proxy))
        captcha = Captcha(self.headers, self.url, self.proxy)
        results = captcha.bypass_captcha()
        if len(results) == 2:
            r = results[1]
            return r
        else:
            return False

    def work(self, r):
        self.soup = BeautifulSoup(r.text, 'lxml')
        self.set_address()
        self.set_hacked_time()
        self.set_proof()
        self.set_notified_by()
        self.set_system()
        self.set_web_server()
        self.set_ip_address()
        self.set_country()
        self.save()
        return True

    def set_address(self):
        domain_containers = self.soup.findAll('li', {'class': 'defaces'})
        for domain_container in domain_containers:
            line = domain_container.text
            if "Domain" in line:
                self.address = '/'.join(line[8:].split('/')[:3])
                return

    def set_hacked_time(self):
        time_containers = self.soup.findAll('li', {'class': 'deface0'})
        hacked_time_str = time_containers[0].text[17:] + ' +0000'
        print('Hacked time: %s' % hacked_time_str)
        self.hacked_time = int(datetime.datetime.strptime(hacked_time_str, "%Y-%m-%d %H:%M:%S %z").timestamp())

    def set_proof(self):
        proof_containers = self.soup.findAll('iframe')
        for proof_container in proof_containers:
            self.proof = proof_container.get('src')
            return

    def set_notified_by(self):
        containers = self.soup.findAll('li', {'class': 'defacef'})
        self.notified_by = containers[0].text[13:]

    def set_system(self):
        containers = self.soup.findAll('li', {'class': 'defacef'})
        self.system = containers[1].text[8:]

    def set_web_server(self):
        containers = self.soup.findAll('li', {'class': 'defaces'})
        self.web_server = containers[1].text[12:]

    def set_ip_address(self):
        containers = self.soup.findAll('li', {'class': 'defacet'})
        self.ip_address = containers[0].text[12:]

    def set_country(self):
        containers = self.soup.findAll('img', title=True)
        for container in containers:
            try:
                self.country = country_code_list[container['title']]
            except:
                print(container['title'])
                self.country = 'US'

    def save(self):
        print(self.address, self.zid, self.proof, self.source,
              self.hacked_time, self.notified_by, self.system,
              self.web_server, self.ip_address, self.country, None)


time_check = time.time()


# last_zid = None


class CrawlerMark:
    def __init__(self, proxy):
        self._proxy = proxy
        self._headers = None
        self._crawler_num = 0

    def start(self):
        self.set_headers()
        global last_zid, time_check
        while self.parse(last_zid):
            if time.time() - time_check < 20 * 60:
                last_zid += 1
            else:
                last_zid = 10000 + 1  # get last id
                time_check = time.time()
        return

    def set_headers(self):
        header = get_headers(self._proxy)
        if header is not None:
            self._headers = header

    def parse(self, zid):
        crawler = Crawler(zid, self._headers, self._proxy, self._crawler_num)
        check = crawler.parse()
        self._crawler_num += 1
        return check


class ZoneHCrawlerManagement:

    def __init__(self):
        pass

    @staticmethod
    def work(proxy):
        cm = CrawlerMark(proxy)
        cm.start()

    def get_proxy(self):
        _proxy_list = list()
        try:
            _proxy_list = ProxiesManagement().parse()
            # _proxy_list = get_gatherproxy()
        except Exception as e:
            print("can't get proxies")
            print(e)
            time.sleep(100)
            self.get_proxy()
        return _proxy_list

    def start(self):
        global last_zid
        last_zid = 10000 + 1  # get last id
        if last_zid != 0:
            for proxy in self.get_proxy()[:50]:
                self.work(proxy)
        # pool = ThreadPool(50)
        # pool.map(self.work, self.get_proxy())
        # pool.wait_completion()
