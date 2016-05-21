#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author = dave.fang@outlook.com
# create = 20160410
import re
import json
import time
import requests
import gevent.pool
import gevent.monkey
from gevent.threadpool import ThreadPool

URI_WY_CORP = "http://www.wooyun.org/corps/page/"
THREAD_NUM = 10
HEADER = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    'Connection': 'keep-alive',
}


class Corp(object):
    def __init__(self):
        self.run = 1
        self.time = int(time.time())

    def start(self):
        offset = 1
        time.sleep(1)
        pool = ThreadPool(THREAD_NUM)
        while self.run:
            offsets = [i + offset for i in range(10)]
            pool.map(self.get_a_list, offsets)
            offset += 10

    def get_a_list(self, offset):
        get_uri = URI_WY_CORP + str(offset)
        while True:
            try_count = 1
            try:
                req = requests.get(get_uri, headers=HEADER, timeout=(15 * try_count))
                content = req.text
                break
            except Exception as e:
                print(str(e))
                try_count += 1
                time.sleep(8)  # in case of the network error
                pass
        self.handle_data(content)

    def handle_data(self, data):
        re_pattern = "<td width=\"370\"><a href=\"/corps/(.*?)\">"
        corps = re.findall(re_pattern, data)
        re_pattern = "<td width=\"370\"><a rel=\"nofollow\" href=\"(.*?)\""
        corps_uri = re.findall(re_pattern, data)
        if len(corps) != len(corps_uri) or len(corps_uri) != 20:
            self.run = 0
        else:
            for i in range(len(corps)):
                data = {
                    'corp_name': corps[i],
                    'corp_url': corps_uri[i],
                    'time': self.time,
                }
                print('[+] {0} \t|\t {1}'.format(corps[i], corps_uri[i]))




if __name__ == '__main__':
    gevent.monkey.patch_socket()
    r = Corp()
    r.start()
    pass
