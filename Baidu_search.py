import json
import time
from multiprocessing import Pool
from pprint import pprint

import jieba
import requests
from lxml import etree
from fake_useragent import UserAgent

ua = UserAgent(path="headers/fake_useragent.json")

headers = {
    'pragma': "no-cache",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.8",
    'upgrade-insecure-requests': "1",
    'user-agent': ua.random,
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'cache-control': "no-cache",
    'connection': "keep-alive",
}

def crawl_baidu_search(keyword, num=8):
    url = "https://www.baidu.com/s?wd=" + keyword
    response = requests.get(url, headers=headers)
    content_tree = etree.HTML(response.text)
    search_data = []
    search_results = content_tree.xpath('//div[@class="result c-container "]')[:10]
    for index, search_result in enumerate(search_results, 1):
        try:
            abstract = search_result.xpath('.//div[@class="c-abstract"]')[0]
            abstract = abstract.xpath('string(.)')
            source = search_result.xpath('.//a[@data-click]')[0]
            source_link = source.xpath('./@href')[0]
            title = source.xpath('string(.)')
            baidu_cache_link = search_result.xpath('.//a[text()="百度快照"]/@href')[0] + "&fast=y"
            search_data.append(
                {
                    'question_id': index,
                    'question': keyword,
                    'title': title,
                    'abstract': abstract,
                    'source_link': source_link,
                    'baidu_cache_link': baidu_cache_link
                }
            )
            if len(search_data) == num:
                break
        except:
            pass
    return search_data


def crawl_baidu_cache_page(url):
    response = requests.get(url, headers=headers)
    response.encoding = 'gbk'
    content_tree = etree.HTML(response.text)
    try:
        raw_content = content_tree.xpath('//div[@style="position:relative"]')[0]
    except:
        return ""
    raw_content = raw_content.xpath('string(.)')
    valid_lines = []
    for line in raw_content.split('\n'):
        line = line.strip()
        if line:
            valid_lines.append(line)
    # valid_content = "。".join(valid_lines)
    valid_content = valid_lines
    return valid_content


def crawl(keyword):
    search_data = crawl_baidu_search(keyword)
    results = []
    pool = Pool(processes=6)
    for each_search_data in search_data:
        results.append(pool.apply_async(crawl_baidu_cache_page, args=(each_search_data['baidu_cache_link'],)))
    pool.close()
    pool.join()
    for each_search_data, result in zip(search_data, results):
        each_search_data['content'] = result.get()
        # each_search_data['doc_tokens'] = list(jieba.cut(each_search_data['content']))
    return search_data


if __name__ == '__main__':
    start_time = time.time()
    data = crawl("北京到上海直线距离")
    with open('spider_example.json', 'w') as wtf:
        for var in data:
            wtf.write(json.dumps(var, ensure_ascii=False)+'\n')
    print(f'耗时: {time.time() - start_time}')