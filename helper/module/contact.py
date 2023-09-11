# -*- coding: utf-8 -*-
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import requests

from helper.settings import *


class Contact:
    def __init__(self):
        self.name = None
        self.address = set()
        self.type = None
        self.black_list = None
        self.source = None

    def get_name(self):
        print(self.name)


class Email(Contact):
    def __init__(self, source):
        super().__init__()
        self.name = 'email'
        self.type = 'person'
        self.source = source
        self.black_list = BLACK_LIST_EMAIL
        self.parse()

    def parse(self):
        # results = re.findall(r'\w+@\w+\.(?:\w+)', self.source)
        results = re.findall(r'[\w\.-]+@[\w\.-]+', self.source)
        if len(results) > 0:
            for mail in results:
                if '.' in mail:
                    if ('jpg' not in mail.lower()) and ('png' not in mail.lower()) \
                            and ('gif' not in mail.lower()) and (mail[-1] is not '.') \
                            and ('.' in mail.split('@')[1]):
                        self.address.add(mail)
        return self.address


class Facebook(Contact):
    def __init__(self, source):
        super().__init__()
        self.name = 'facebook'
        self.type = ''
        self.source = source
        self.black_list = BLACK_LIST_FACEBOOK
        self.start_list = ('https://facebook', 'https://www.facebook', 'facebook', 'www.facebook')
        self.parse()

    def parse(self):
        soup = BeautifulSoup(self.source, 'lxml')
        for elem in soup.find_all("a", href=True):
            link = (elem['href']).lower()
            if link.startswith(tuple(self.start_list)):
                if check_in_blacklist(urlparse(link).path, self.black_list):
                    if 'group' in urlparse(link).path:
                        if link.count('/') == 4 and '?' not in link:
                            self.address.add(link)
                            self.type = 'Group'
                    else:
                        if link.count('/') == 3 and '?' not in link:
                            self.address.add(link)
                            self.type = 'Person'
        return self.address


class Twitter(Contact):
    def __init__(self, source):
        super().__init__()
        self.name = 'twitter'
        self.type = 'person'
        self.source = source
        self.black_list = BLACK_LIST_FACEBOOK
        self.start_list = ('https://twitter', 'https://www.twitter', 'twitter', 'www.twitter')
        self.parse()

    def parse(self):
        soup = BeautifulSoup(self.source, 'lxml')
        for elem in soup.find_all("a", href=True):
            link = (elem['href']).lower()
            if link.startswith(tuple(self.start_list)):
                if check_in_blacklist(urlparse(link).path, self.black_list):
                    if link.count('/') == 3 and '?' not in link:
                        if '.' not in urlparse(link).path:
                            self.address.add(link)
        return self.address


def check_in_blacklist(path, blacklist):
    check = True
    search_file = open(blacklist)
    for line in search_file:
        if path in line:
            check = False
    return check
