import requests
import time
import json

from cybot.helper.settings import *
from cybot.helper.cylog import CyLog


class Hack:
    def __init__(self, id=None, website_id=None):
        self.id = id
        self.website_id = website_id

    @staticmethod
    def get_proof_address(url):
        proof_list = list()
        r = requests.get(url, headers=API_HEADERS, timeout=20).json()
        if r['count'] == 0:
            CyLog.info('Status crawler: sleep time!')
            time.sleep(20 * 60)
        else:
            for obj in r['results']:
                data = {
                    'proof': obj['proof'],
                    'hack_id': obj['id'],
                    'website_id': obj['website']
                }
                proof_list.append(data)
        return proof_list

    def update_hack(self):
        data = {
            'is_checked_status': True,
        }
        requests.patch('%s%s/' % (API_HACK_URL, self.id), headers=API_HEADERS, data=data)
        return

    def get_hack_info(self):
        try:
            r = requests.get('%s%s%s' % (API_HACK_URL, '?website=', self.website_id), headers=API_HEADERS).json()
            return r['results'][0]
        except:
            CyLog.info("Can't connect to API")
            time.sleep(10)
            self.get_hack_info()


class Website:
    def __init__(self, id=None, page=None):
        self.id = id
        self.page = page

    @staticmethod
    def post_hacked_website(address, zid, proof, source, hacked_time,
                            notified_by, system, web_server, ip_address, country, mid):
        try:
            data = [{"address": address,
                     "meta_data":
                         {
                             "zid": zid,
                             "proof": proof,
                             "source": source,
                             "hacked_time": hacked_time,
                             "notified_by": notified_by,
                             "system": system,
                             "web_server": web_server,
                             "ip_address": ip_address,
                             "country": country,
                             "mid": mid
                         }
                     }]
            r = requests.post(API_WEBSITE_URL, headers=API_HEADERS, json=data)
            return r.status_code
        except requests.exceptions.ConnectionError:
            CyLog.error("Can't connect to API")
        except ValueError:
            print('error')

    def get_website(self):
        r = requests.get('%s%s/' % (API_WEBSITE_URL, self.id), headers=API_HEADERS, timeout=20).json()
        return r['address']

    def update_status(self, status):
        data = {
            'status': status
        }
        requests.patch('%s%s/' % (API_WEBSITE_URL, self.id), headers=API_HEADERS, data=data, timeout=20)
        return

    def get_websites_list(self):
        try:
            r = requests.get(API_TECH_CRAWLER_URL, headers=API_HEADERS, timeout=20).json()
            if len(r['results']) == 0:
                CyLog.info('Tech crawler: sleep time!')
                time.sleep(20 * 60)
                self.get_websites_list()
            return r['results']
        except requests.exceptions.ConnectionError:
            CyLog.error("Can't connect to API")

    def update_tech(self, tech):
        try:
            cms = tech['cms'][0]['name']
        except:
            cms = None
        try:
            language = tech['programming_languages'][0]['name']
        except:
            language = None
        try:
            data = {
                'updated_time': int(time.time()),
                'technology': json.dumps(tech),
                'is_crawled_tech': True,
                'cms': cms,
                'language': language,
            }
            # print(data)
            requests.patch(API_WEBSITE_URL + '%s/' % self.id, headers=API_HEADERS, data=data, timeout=20)
        except requests.exceptions.ConnectionError:
            CyLog.error("Can't connect to API")

    def get_contact_crawler_url(self):
        try:
            websites_crawling_list = list()
            r = requests.get(API_CONTACT_CRAWLER_URL, headers=API_HEADERS).json()
            if len(r['results']) == 0:
                time.sleep(20 * 60)
                self.get_contact_crawler_url()
            for i in range(0, len(r['results'])):
                obj_website = {'id': r['results'][i]['id'],
                               'address': r['results'][i]['address'],
                               'updated_time': r['results'][i]['created_time']}
                websites_crawling_list.append(obj_website)
            return websites_crawling_list
        except Exception as e:
            print(e)
            CyLog.info("Can't connect to API")
            time.sleep(100)
            self.get_contact_crawler_url()

    def update_crawled_contact(self):
        try:
            data = {
                'is_crawled_contact': True
            }
            r = requests.patch('%s%s/' % (API_WEBSITE_URL, self.id), headers=API_HEADERS, data=data)
        except:
            CyLog.info("Can't connect to API")
            time.sleep(10)
            self.update_crawled_contact()


class Contact:
    def __init__(self, web_id, name=None, address=None, type=None,
                 secret_key=None, vi=None, affected_url=None, detected_time=None):
        self.web_id = web_id
        self.name = name
        self.address = address
        self.type = type
        self.secret_key = secret_key
        self.vi = vi
        self.affected_url = affected_url
        self.detected_time = detected_time

    def post(self):
        try:
            data = {
                'name': self.name,
                'address': self.address,
                'type': self.type,
                'website': self.web_id,
                'created_time': int(time.time()),
                'secret_key': self.secret_key,
                'vi': self.vi,
                'affected_url': self.affected_url,
                'detected_time': self.detected_time
            }
            r = requests.post(API_WEBSITE_URL + str(self.web_id) + '/contacts/', headers=API_HEADERS, data=data)
        except:
            CyLog.info("Can't connect to API")
            time.sleep(10)
            self.post()


# zone-h
def get_last_zid():
    r = requests.get(API_ZID_URL, headers=API_HEADERS).json()
    # print(r)
    if int(time.time()) - r['results'][0]['hacked_time'] < 60 * 60:
        CyLog.info('Zone-H crawler: sleep time!')
        time.sleep(60 * 60)
    last_zid = int(r['results'][0]['zid'])
    return last_zid


# mirror-h
def get_last_mid():
    r = requests.get(API_MID_URL, headers=API_HEADERS).json()
    last_mid = int(r['results'][0]['mid'])
    return last_mid


# proxies
def post_proxies(proxies_list):
    try:
        r = requests.post(API_PROXIES_URL, headers=API_HEADERS, json=proxies_list)
        return r.status_code
    except requests.exceptions.ConnectionError:
        CyLog.error("Can't connect to API")


def get_proxies():
    try:
        r = requests.get(API_PROXIES_URL, headers=API_HEADERS).json()
        return r
    except requests.exceptions.ConnectionError:
        CyLog.error("Can't connect to API")


def delete_proxy(proxy_id):
    try:
        r = requests.delete(API_PROXIES_URL + '%s/' % proxy_id, headers=API_HEADERS)
        return r.status_code
    except requests.exceptions.ConnectionError:
        CyLog.error("Can't connect to API")
