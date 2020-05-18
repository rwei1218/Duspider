#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import urllib.request
import zlib
from urllib import parse, request

from lxml import etree
from tqdm import tqdm

from ip_pool import IP_pool


class BaiduBaike():
    def __init__(self):
        """
        Items:
        - extract_fun_dict  ##页面解析函数集合
        """
        self.extract_func_dict = {
            "infobox": self.extract_info_box,
            "summary": self.extract_summary             
        }
        self.headers = {
            "Accept-Encoding": "Gzip",  # 使用gzip压缩传输数据让访问更快
        }
        self.IP_pool = IP_pool()
        self.ip_list = []

    def get_html_local(self, url):
        """
        以本地IP获取html页面
        """
        return request.urlopen(url).read().decode('utf-8').replace('&nbsp;', '')

    def get_html_proxy(self, url, ip):
        """
        以代理IP获取html页面
        """
        proxies = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': self.IP_pool.username, 'pwd': self.IP_pool.password, 'proxy': ip},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': self.IP_pool.username, 'pwd': self.IP_pool.password, 'proxy': ip}
        }

        proxy_hander = urllib.request.ProxyHandler(proxies)
        opener = urllib.request.build_opener(proxy_hander)

        req = urllib.request.Request(url, headers=self.headers)

        result = opener.open(req)
        print('connection code: ', result.status)  # 获取Response的返回码

        content_encoding = result.headers.get('Content-Encoding')
        if "gzip" in content_encoding:
            return zlib.decompress(result.read(), 16 + zlib.MAX_WBITS).decode('utf-8').replace('&nbsp;', '') # 获取页面内容
        else:
            return result.read().decode('utf-8').replace('&nbsp;', '') # 获取页面内容

    def extract_info_box(self, selector):
        """
        抽取百度百科的info box
        """
        info_data = {}
        if selector.xpath('//h2/text()'):
            info_data['current_semantic'] = selector.xpath('//h2/text()')[0].replace('    ', '').replace('（','').replace('）','')
        else:
            info_data['current_semantic'] = ''
        if info_data['current_semantic'] == '目录':
            info_data['current_semantic'] = ''

        tags = [item.replace('\n', '') for item in selector.xpath('//span[@class="taglist"]/text()')]
        info_data['tags'] = []
        for tag in tags:
            if tag != '':
                info_data['tags'].append(tag)
        if selector.xpath("//div[starts-with(@class,'basic-info')]"):
            for li_result in selector.xpath("//div[starts-with(@class,'basic-info')]")[0].xpath('./dl'):
                attributes = [attribute.xpath('string(.)').replace('\n', '') for attribute in li_result.xpath('./dt')]
                values = [value.xpath('string(.)').replace('\n', '') for value in li_result.xpath('./dd')]
                for item in zip(attributes, values):
                    info_data[item[0].replace('    ', '')] = item[1].replace('    ', '')
        return info_data

    def extract_summary(self, selector):
        """
        抽取百度百科的summary
        """
        info_data = {}
        if selector.xpath('//h2/text()'):
            info_data['current_semantic'] = selector.xpath('//h2/text()')[0].replace('    ', '').replace('（','').replace('）','')
        else:
            info_data['current_semantic'] = ''
        if info_data['current_semantic'] == '目录':
            info_data['current_semantic'] = ''

        tags = [item.replace('\n', '') for item in selector.xpath('//span[@class="taglist"]/text()')]
        info_data['tags'] = []
        for tag in tags:
            if tag != '':
                info_data['tags'].append(tag)
        if selector.xpath("//div[starts-with(@class,'lemma-summary')]"):
            paras = []
            for li_result in selector.xpath("//div[starts-with(@class,'lemma-summary')]")[0].xpath('./div'):
                para = li_result.xpath('string(.)').replace('\n', '')
                paras.append(para)    
        info_data['paras'] = paras
        return info_data

    def checkbaidu_polysemantic(self, selector, extract_func, proxy):
        """
        对一个关键词对多个语义进行爬取
        """
        semantics = ['https://baike.baidu.com' + sem for sem in
                     selector.xpath("//ul[starts-with(@class,'polysemantList-wrapper')]/li/a/@href")]
        names = [name for name in selector.xpath("//ul[starts-with(@class,'polysemantList-wrapper')]/li/a/text()")]
        info_list = []
        if semantics:
            for item in zip(names, semantics):
                if proxy:
                    selector = etree.HTML(self.get_html_proxy(item[1], random.choice(self.ip_list)))
                else:
                    selector = etree.HTML(self.get_html_local(item[1]))
                info_data = extract_func(selector)
                info_data['current_semantic'] = item[0].replace('    ', '').replace('（','').replace('）','')
                if info_data:
                    info_list.append(info_data)
        return info_list

    def extract_baidu(self, word, mode, polysemantic=False, proxy=False):
        """
        主函数
        """
        url = "http://baike.baidu.com/item/%s" % parse.quote(word)
        extract_func = self.extract_func_dict[mode]
        if proxy:
            self.ip_list = self.IP_pool.get_ip_list()
            selector = etree.HTML(self.get_html_proxy(url, random.choice(self.ip_list)))
        else:
            selector = etree.HTML(self.get_html_local(url))
        info_list = list()
        info_list.append(extract_func(selector))
        if polysemantic:
            polysemantics = self.checkbaidu_polysemantic(selector, extract_func, proxy)
            if polysemantics:
                info_list += polysemantics
        infos = [info for info in info_list if len(info) > 2]

        return infos


class Test(object):
    def __init__(self):
        self.baidu = BaiduBaike()
        self.word = "石家庄"

    def test_extract_infobox(self):
        print("Extract infobox.")
        passage = self.baidu.extract_baidu(
            word=self.word,
            mode="infobox",
            polysemantic=False,
            proxy=False
        )
        print("Passage: ", passage)

    def test_extract_summary(self):
        print("Extract summary.")
        passage = self.baidu.extract_baidu(
            word=self.word,
            mode="summary",
            polysemantic=False,
            proxy=False
        )
        print("Passage: ", passage)

    def test_extract_proxy(self):
        print("Extract summary with proxy.")
        passage = self.baidu.extract_baidu(
            word=self.word,
            mode="summary",
            polysemantic=False,
            proxy=True
        )
        print("Passage: ", passage)

    def test_extract_polysemantic(self):
        print("Extract summary for all semantic.")
        passage = self.baidu.extract_baidu(
            word=self.word,
            mode="summary",
            polysemantic=True,
            proxy=False
        )
        print("Passage: ", passage)



if __name__ == "__main__":

    # crawler test
    test_processor = Test()
    test_processor.test_extract_infobox()
    test_processor.test_extract_summary()
    test_processor.test_extract_proxy()
    test_processor.test_extract_polysemantic()

