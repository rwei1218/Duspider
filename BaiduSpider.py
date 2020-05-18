import json

import re

import bs4
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from fake_useragent import UserAgent

from urllib import parse

from ip_pool import IP_pool

class BaiduBaike(object):
    def __init__(self):
        self.url = "http://baike.baidu.com/item"
        self.timeout = 10
        self.ua = UserAgent(path="headers/fake_useragent.json")
        self.parser = 'html.parser'

    def get_html_local(self, url, headers=None):
        try:
            web_response = requests.get(url, headers=headers, timeout=self.timeout)
            web_response.raise_for_status()
            # print(web_response.encoding)
            # print(web_response.apparent_encoding)
            web_response.encoding = web_response.apparent_encoding
            return web_response.text
        except Exception as e:
            return e

    def get_html_proxy(self, url, proxy_ip, headers=None):
        pass

    def head_parse(self, soup):
        """
        - Intro: 解析百科页面的header
        - Return:
            - title: 百度百科标题
            - description: 百度百科的一段描述性文字
            - keywords: 百度检索的关键词，这类关键词都会指向该百科词条
        """
        title = soup.head.title.string
        description = soup.head.find('meta', attrs = {'name': 'description'})
        keywords = soup.head.find('meta', attrs = {'name': 'keywords'})
        head = {}
        head['title'] = title
        head['description'] = description['content'] if description != None else None
        head['keywords'] = keywords['content'] if keywords != None else None
        head['keywords_list'] = head['keywords'].split(' ')
        return head

    def tag_parse(self, soup):
        """
        - Intro: 解析百度百科词条的tag
        - Return:
            - tags: 该百科词条的一些属性值
        """
        tags = soup.body.find_all('span', attrs = {'class': 'taglist'})
        tags = [tag.text.strip() for tag in tags]
        return tags

    def info_box_parse(self, soup):
        """
        - Intro: 定向解析百科词条的info box
        - Return:
            - 返回一个字典，对应百科中的infobox
        """
        info_items = soup.body.find_all('dl', attrs = {'class': re.compile(r'^basicInfo-block')})
        info_data = {}
        for info_item in info_items:
            attributes = [item.text.replace('\xa0', '').strip('') for item in info_item.find_all('dt')] 
            values = [item.text.replace('\n', '').strip('') for item in info_item.find_all('dd')]
            for item in zip(attributes, values):
                info_data[item[0]] = item[1]
        return info_data

        
    def content_summary_parse(self, soup):
        """
        - Intro: 定向解析百科词条中的summary片段
        - Return:
            - 
        """
        summary_items = soup.body.find_all('div', attrs = {'class': ''})

    def craw(self, word):
        url = self.url + '/%s' % parse.quote(word)
        # url = "http://python123.io/ws/demo.html"
        print(url)
        headers = {"User-Agent":self.ua.random}
        print(headers)
        web_text = self.get_html_local(url, headers=headers)
        # print(web_response)
        soup = BeautifulSoup(web_text, self.parser)
        # print(soup.head)
        # print(soup.head.meta.attrs)
        # print(soup.head.meta.string)
        # print(soup.head.find('meta', attrs={'name':'description'}))
        # print(soup.head.find('meta', attrs={'name':'description'})['content'])
        # print(soup.body.find('span', attrs = {'class': 'taglist'}))

        # for item in soup.body.find_all('span', attrs = {'class': 'taglist'}):
        #     print(item.text.strip())
        #     print(item.a)

        # print(self.tag_parse(soup))
        # self.info_box_parse(soup)

        # print(soup.body.find('dl', attrs = {'class': re.compile(r'^basicInfo-block')}))

        # print(self.head_parse(soup))

        summ = soup.body.find('div', attrs={'class': 'lemma-summary'})
        for item in summ.contents:
            print('item: ', item)
        print(len(summ.contents))
        print(type(summ))

        return self.head_parse(soup)




if __name__ == "__main__":
    word = "北京理工大学"
    Baike_processor = BaiduBaike()
    result = Baike_processor.craw(word)
    # with open('result.json', 'w', encoding='utf8') as wtf:
    #     wtf.write(json.dumps(result, ensure_ascii=False))

    print('end')