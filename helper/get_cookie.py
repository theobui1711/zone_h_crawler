import binascii
import requests
from helper import aes
from helper.settings import EXPIRED_COOKIE_SIGN, ZONE_H_ROOT


def to_numbers(_string):
    e = bytearray(binascii.unhexlify(_string))
    f = [int(i) for i in e]
    return f


def to_hex(_number):
    code = ''
    for i in _number:
        if len(hex(i)) == 3:
            code = code + '0' + hex(i)[2:]
        else:
            code += hex(i)[2:]
    return code


def get_cookie(html):
    code = []
    for text in html.split("+"):
        if "=toNumbers(" in text:
            for text2 in text.split("=toNumbers("):
                if "return" not in text2:
                    code.append(text2[1:33])
    a = to_numbers(code[0])
    b = to_numbers(code[1])
    c = to_numbers(code[2])
    moo = aes.AESModeOfOperation()
    d = moo.decrypt(cipherIn=c, originalsize=32, mode=2, key=a, size=moo.aes.keySize["SIZE_128"], IV=b)
    # cookie = "__utmz=1.1530094147.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); ZHE=%s; PHPSESSID=6r0aorud5665fq82qp8kb9n701;" \
    #          " __utma=1.431770674.1530094147.1541398433.1541662745.144; __utmc=1; __utmb=1.6.10.1541662745" % to_hex(d)
    cookie = "ZHE=%s" % to_hex(d)
    return cookie


def get_headers(proxy):
    try:
        headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            #               '(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            # 'Accept-Language': 'vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3',
            # 'Content-Type': 'application/json',
            # 'Pragma': 'no-cache'
        }
        r = requests.get(ZONE_H_ROOT, proxies=proxy, headers=headers, timeout=10)
        cookie = None
        if EXPIRED_COOKIE_SIGN in r.text:
            cookie = get_cookie(r.text)
        if not cookie:
            return None
        headers['Cookie'] = cookie
        return headers
    except Exception as e:
        print(e)
        return None
