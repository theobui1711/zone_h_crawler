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
print(proxy_list)
for proxy_ in proxy_list:
    print(proxy_)
    try:
        header = get_headers(proxy_)
        if header:
            crawler = CaptchaCollection(header, proxy_)
            crawler.get_captcha()
            break
    except Exception as e:
        print(e)
