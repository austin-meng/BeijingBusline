from selenium import webdriver
import time
import re
import requests
import os
import csv


class BusData:
    # get bus data
    def __init__(self,outdir):
        self.outdir = outdir
        self.error_busno = []
        error_fn = self.outdir + '\\%s.txt' % time.strftime('%Y%m%d%H%M%S',time.localtime())
        # print(error_fn)
        self.logfile = open(error_fn,'w',encoding='utf-8')
        self.csv_writer = csv.writer(self.logfile)
        
    def __del__(self):
        # record error busline number
        if len(self.error_busno)>0:
            print('can not get busno:{}'.format(self.error_busno))
            self.csv_writer.writerow(self.error_busno)
        else:
            self.logfile.write('Get All Busline Data!')
            print('Get All Busline Data!')
        self.logfile.close()

    def get_busnofiles(self):
        # all busline number file path
        busnopath = r'C:\Users\china\Desktop\busline\BusNo'
        filelist = []
        for root,dirs,files in os.walk(busnopath):
            for file in files:
                fn = os.path.join(root,file)
                filelist.append(fn)
        # print(filelist)
        return filelist

    def get_busno(self,file):
        busno_list = []
        with open(file,'r',encoding='utf-8') as f:
            busno_list = f.read().strip().split(',')
        # print(busno_list)
        return busno_list

    def get_lineID(self,busno,flag):
        # 北京公交网
        url = 'http://www.bjbus.com/map/index.php?uSec=00000160&uSub=00000161#c=12956000,4824875,10&hb=0,1'
        driver = webdriver.PhantomJS()
        driver.get(url)
        time.sleep(0.1)
        ele_input = driver.find_element_by_id('businfo_tb_key')
        # search busline
        ele_input.send_keys(busno)
        time.sleep(0.1)
        search_btn = driver.find_element_by_id('businfo_tb_submit')
        search_btn.click()
        time.sleep(0.1)
        # 往返
        # lineinfo_eles = driver.find_elements_by_class_name('businfo_line')
        # print(type(lineinfo_eles))
        # print(len(lineinfo_eles))
        # lineid_list = []
        # for idx,ele in enumerate(lineinfo_eles[:2]):
        #     try:
        #         lineid = ele.get_attribute('id')
        #         lineid = re.findall(r'line_(\d+)',lineid)[0]
        #         lineid_list.append(lineid)
        #     except:
        #         print('can not get lineID of {0}-{1}'.format(busno,idx))
        #         driver.quit()
        #         self.error_busno.append(busno)
        #         return ''            
        # 单程
        flag = int(flag)
        try:
            if flag == 0:
                lineidinfo_ele = driver.find_element_by_class_name('businfo_line')  # 往
            if flag == 1:
                lineidinfo_ele = driver.find_elements_by_class_name('businfo_line')[1]  # 返
            lineid = lineidinfo_ele.get_attribute('id')
            lineid = re.findall(r'line_(\d+)',lineid)[0]
            driver.quit()
            return lineid
        except:
            print('can not get lineID of {0}'.format(busno))
            driver.quit()
            self.error_busno.append(busno)
            return ''

    def get_json(self,busno,lineid,outfn):
        url = 'http://api.go2map.com/engine/api/linedetail/json?hidden_MapTool=busex2.BusLineClustringList&lineid=%s& \
                fromuser=bjbus&datasource=bjbus&clientid=9db0f8fcb62eb46c&cb=SGS.BUSINFO_DETAIL15b19065310b' % (lineid)        
        try:
            r = requests.get(url,timeout=30)
            r.raise_for_status
            r.encoding = r.apparent_encoding
            result = r.text
            # driver = webdriver.PhantomJS()
            # driver.get(url)
            # result = driver.page_source
            try:
                with open(outfn,'w',encoding='utf-8') as f:
                    f.write(result[130:-1])
                    print('get {}.'.format(busno))
            except:
                print('write {} error!'.format(outfn))
                self.error_busno.append(busno)
        except:
            print('get json error! busno:{}'.format(busno))
            self.error_busno.append(busno)

    def run(self,flag):
        files = self.get_busnofiles()
        for f in files:
            busno_list = self.get_busno(f)
            for busno in busno_list:
                outfn = self.outdir + "\\%s-%s.txt" % (busno,flag)
                if os.path.exists(outfn):
                    print('{} already exists!'.format(outfn))
                    continue
                lineid = self.get_lineID(busno,flag)             
                if len(lineid) > 0:                                        
                    self.get_json(busno,lineid,outfn)  


if __name__ == '__main__':
    t1 = time.perf_counter()
    outdir = r"C:\Users\china\Desktop\busline\busdata_come" # 返
    busdata = BusData(outdir)
    # flag: 0往 1返
    flag = '1'
    busdata.run(flag)
    t2 = time.perf_counter()
    print('spider run time:{:.2f}s'.format(t2-t1))