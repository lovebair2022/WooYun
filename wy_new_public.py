#!/usr/bin/env python3
# coding=utf-8
# author=dave.fang@outlook.com
# create=20160518
import re
import gevent
import datetime
import requests
from gevent.threadpool import ThreadPool

WOOYUN_CONFIRM = 'http://www.wooyun.org/bugs/new_confirm/page/'
WOOYUN_BUG_DETAIL = 'http://www.wooyun.org/bugs/'
POOL_THREADS = 50
HEADER = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
}


class Cloud:
    def __init__(self):
        self.pool = ThreadPool(POOL_THREADS)
        self.bugs = []
        self.have_content = True
        pass

    def get_one_page(self, page_id):
        print('[*] Crawl Page: {0}'.format(str(page_id)))
        page_url = WOOYUN_CONFIRM + str(page_id)
        while True:
            try:
                req = requests.get(page_url, headers=HEADER, timeout=15)
                if req.status_code == 200:
                    break
            except Exception as e:
                print('[-] Page: {0} Get Error: {1}'.format(str(page_id), str(e)))
        self.analyse_content(req.text)

    def analyse_content(self, content):
        try:
            reg_pattern = '<tr>\s(.*)\s(.*)\s(.*)\s(.*)\s(.*)\s(.*)\s'
            tmp = re.findall(reg_pattern, content)
            if len(tmp) <= 1:
                self.have_content = False
                return
            for tmp_one in tmp:
                # print(tmp_one)
                bug_info = {}
                reg_pattern = '<th>(.*?)</th>'
                bug_date = re.findall(reg_pattern, tmp_one[1])
                if len(bug_date) > 0:
                    bug_info['date'] = bug_date[0]
                    reg_pattern = '<a href="/bugs/(.*?)">(.*?)</a>'
                    bug_info_tmp = re.findall(reg_pattern, tmp_one[2])
                    bug_info_tmp = bug_info_tmp[0]
                    bug_info['id'] = bug_info_tmp[0]
                    bug_info['name'] = bug_info_tmp[1]
                    self.get_bug_detail(bug_info_tmp[0], bug_info)
                    self.bugs.append(bug_info)
        except Exception as e:
            print('[-] Analyse Error! Detail: {0}'.format(str(e)))

    @staticmethod
    def get_bug_detail(bug_id, bug_info):
        page_url = WOOYUN_BUG_DETAIL + str(bug_id)
        while True:
            try:
                req = requests.get(page_url, headers=HEADER, timeout=15)
                if req.status_code == 200:
                    break
            except Exception as e:
                print('[-] BUG: {0} Get Error: {1}'.format(str(bug_id), str(e)))
        content = req.text
        reg_pattern = '<p class="detail">漏洞Rank：(.*?)</p>'
        bug_info_tmp = re.findall(reg_pattern, content)
        bug_info['rank'] = bug_info_tmp[0].strip()
        reg_pattern = '<h3 class=\'wybug_corp\'>相关厂商：(.*)\s(.*?)</a>'
        bug_info_tmp = re.findall(reg_pattern, content)
        bug_info['corp'] = bug_info_tmp[0][0].strip() + bug_info_tmp[0][1].strip()

    def start(self):
        i_count = 1
        while self.have_content:
            self.pool.map(self.get_one_page, [x for x in range(i_count, i_count + 50)])
            gevent.wait()
            i_count += 50
        print(self.bugs)
        file_handle = open('wy_no_1.csv', 'w')
        file_handle.write('bug_id, rank, name, corp, date\n')
        for one_bug in self.bugs:
            file_handle.write('{0}, {1}, {2}, {3}, {4}\n'.
                              format(one_bug['id'], one_bug['rank'], one_bug['name'], one_bug['corp'], one_bug['date']))
            print(one_bug)
        file_handle.close()


if __name__ == '__main__':
    print('[*] WooYun Crawler No.1')
    start_time = datetime.datetime.now()
    cloud = Cloud()
    cloud.start()
    # cloud.get_one_page(1)
    end_time = datetime.datetime.now()
    print('[*] Total Time Consumption: ' + str((end_time - start_time).seconds) + 's')
