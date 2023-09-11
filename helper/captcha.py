import requests
# from python_anticaptcha import AnticaptchaClient, ImageToTextTask

from helper.settings import *


class Captcha:
    def __init__(self, headers, url, proxy):
        self.headers = headers
        self.proxy = proxy
        self.url = url
        self.captcha_image = None
        self.captcha_text = None

    def bypass_captcha(self):
        self.get_captcha(self.headers)

        # job = self.get_captcha_text()
        # captcha_text = job.get_captcha_text()

        captcha_text = input('Enter captcha: ')

        data = {"captcha": "%s" % captcha_text}
        r = requests.post(url=self.url, headers=self.headers,
                          proxies=self.proxy, data=data)
        if CAPTCHA_SIGN not in r.text:
            print("Bypass successful!")
            return True, r
        else:
            print("In put Captcha is incorrect, Try again!")
            # job.report_incorrect()
            return False, r

    def get_captcha(self, headers):
        captcha_request = requests.get(CAPTCHA_LINK, headers=headers, proxies=self.proxy)
        if captcha_request.status_code == 200:
            with open(CAPTCHA_IMG, 'wb') as f:
                f.write(captcha_request.content)

    @staticmethod
    def get_captcha_text():
        pass
        # api_key = ANTI_CAPTCHA_API_KEY
        # captcha_fp = open(CAPTCHA_IMG, 'rb')
        # client = AnticaptchaClient(api_key)
        # task = ImageToTextTask(captcha_fp)
        # job = client.createTask(task)
        # job.join()
        # return job
