#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request
import zlib
import ssl
import json
import random
from urllib import parse

ssl._create_default_https_context = ssl._create_unverified_context  # 全局取消证书验证，避免访问https网页报错

class IP_pool(object):
    def __init__(self):
        #  api接口，返回格式为json
        self.api_url = 'http://dps.kdlapi.com/api/getdps/?orderid=998357268078587&num=1&pt=1&format=json&sep=1'

        # 用户名和密码(私密代理/独享代理)
        self.username = "????"
        self.password = "????"

    def get_ip_list(self):
        # 返回可用的ip List
        response = urllib.request.urlopen(self.api_url)
        json_dict = json.loads(response.read().decode('utf-8'))
        ip_list = json_dict['data']['proxy_list']

        return ip_list

class Test(object):
    def __init__(self):
        self.ip_pool = IP_pool()

    def test_ip_list(self):
        ip_list = self.ip_pool.get_ip_list()
        print("Test IP List: ", ip_list)


if __name__ == "__main__":
    test_processor = Test()
    test_processor.test_ip_list()
    