import requests
from bs4 import BeautifulSoup

from helper.proxies.proxies_crawler import ProxiesManagement
from helper.get_cookie import get_headers
from helper.settings import *


class CaptchaCollection:
    def __init__(self, headers, proxy):
        self.url = CAPTCHA_LINK
        self.headers = headers
        self.proxy = proxy

    def get_captcha(self):
        r = requests.get(self.url, headers=self.headers, proxies=self.proxy)
        if r.status_code == 200:
            print(r.content)
            with open(CAPTCHA_IMG, 'wb') as f:
                f.write(r.content)


proxy_list = ProxiesManagement().parse()
for proxy in proxy_list:
    count = 0
    header = get_headers(proxy)
    if header:
        crawler = CaptchaCollection(header, proxy)
        crawler.get_captcha()
        break
