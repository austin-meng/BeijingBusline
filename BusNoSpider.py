import requests
from bs4 import BeautifulSoup
import re
import os
import csv
import time


class BusLineListSpider:
    def __init__(self):
        pass

    def getHTML(self,url):
        try:
            r = requests.get(url,timeout=30)
            r.raise_for_status()
            # r.encoding = r.apparent_encoding
            r.encoding = 'gbk'
            return r.text
        except:
            return ""

    def parsePage(self,html):
        linelist = []
        soup = BeautifulSoup(html,'html.parser')
        dd_tag = soup.find('div',{'class':'inforB pad10'}).find('dd')
        for a in dd_tag.find_all('a'):
            line = a.string.strip()
            linelist.append(line)
        return linelist

    def store(self,i,linelist):
        fpath = 'BusLines_%s.txt' % str(i)
        if os.path.exists(fpath):
            print('%s already exists!' % fpath)
            pass
        else:
            with open(fpath,'w',encoding='utf-8') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(linelist)
                # print('save %s' % fpath)

    def run(self):
        # start_num = range(1,10)
        start_num = list(range(1,10)) + ['B','C','D','E','F','G','H',\
                                         'J','K','L','M','N','P','S',\
                                         'T','X','Y','Z']
        pages = len(start_num)   
        for idx,i in enumerate(start_num):
            url = "http://bus.mapbar.com/beijing/xianlu_" + str(i)
            html = self.getHTML(url)
            linelist = self.parsePage(html)
            # self.store(i,linelist)
            print('\rrate of process:{:.2f}%'.format(idx/pages*100.0),end='')


if __name__ == '__main__':
    t1 = time.perf_counter()
    bus = BusLineListSpider()
    bus.run()
    t2 = time.perf_counter()

    print('\nrun time:{:.2f}s'.format(t2-t1))
