import requests
from bs4 import BeautifulSoup

from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)

class Proxy:
    def __init__(self, soup):
        self.soup = soup
        self.proxy = None
        self.ip_address = None
        self.port = None
        self.https = None

    def set_proxy(self):
        source = self.soup.findAll('td')
        self.ip_address = source[0].text
        self.port = source[1].text
        self.https = source[6].text
        if self.https == 'no':
            self.proxy = {
                'http': 'http://%s:%s' % (self.ip_address, self.port),
            }
            return self.proxy
        return None


class ProxiesManagement:
    def __init__(self):
        self.proxies_queue = list()

    def work(self, url):
        r = requests.get(url, verify=False)
        soup = BeautifulSoup(r.text, 'lxml')
        containers = soup.findAll('tr')
        for container in containers:
            if ('IP Address' not in container.text) and \
                    ('Working' not in container.text) and \
                    ('no' in container.text) or ('yes' in container.text):
                proxy = Proxy(container).set_proxy()
                if proxy is not None \
                        and proxy not in self.proxies_queue:
                    self.proxies_queue.append(proxy)

    def parse(self):
        self.work('https://free-proxy-list.net/')
        self.work('https://www.us-proxy.org/')
        self.work('https://free-proxy-list.net/anonymous-proxy.html')
        self.work('https://www.socks-proxy.net/')
        self.work('https://www.sslproxies.org/')
        return self.proxies_queue
