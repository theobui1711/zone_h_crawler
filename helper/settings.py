import os
import configparser
import ast
import csv

ENVIRONMENT = "dev"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, 'conf', '%s.ini' % ENVIRONMENT)

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# thread
STATUS_CHECKER_THREAD = int(config['Thread']['StatusCheckerNumber'])
TECH_CRAWLER_THREAD = int(config['Thread']['TechCrawlerNumber'])

# wappalyzer
WAPPALYZER_DATA = os.path.join(BASE_DIR, 'data', '%s' % config['Data']['Wappalyzer'])

# cache tool
CACHE_TOOL = config['CacheTool']['URL']

# zone-h
ZONE_H_ROOT = config['ZoneH']['Root']
ZONE_H_MIRROR = ZONE_H_ROOT + config['ZoneH']['Mirror']
CAPTCHA_SIGN = config['ZoneH']['CaptchaSign']
EXPIRED_COOKIE_SIGN = config['ZoneH']['Cookie']
FIRST_START_ID = config['ZoneH']['FirstStart']
CAPTCHA_LINK = config['ZoneH']['CaptchaURL']
EMPTY_SIGN = config['ZoneH']['EmptySign']
BLOCK_SIGN = config['ZoneH']['BlockSign']

# mirror-h
MIRROR_H_URL = config['MirrorH']['URL']
API_MID_URL = config['MirrorH']['MID_URL']

# captcha image
CAPTCHA_IMG = os.path.join(BASE_DIR, 'data', '%s' % config['ZoneH']['CaptchaImage'])

# time
DELETE_TIME = int(config['Time']['DeleteTime'])
SLEEP_TIME = int(config['Time']['SleepTime'])
