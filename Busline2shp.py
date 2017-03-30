import json
from ArcgisShape import Shape
from osgeo import ogr, osr
import re
import time
import os
from BuslineSpider import BusData

# 线图层（线，线路号busno 936，起点站stop0，终点站stop1，往返方向？，ID，ID_,）
# 点图层（点，点号stoporder,站名stopname，线路号busno，ID，)

class BusLineShp:
    # generate shapefile of bus_line and bus_stop
    def __init__(self,datadir,outpath):
        # dx,dy = (84.57977183535695,329.83781695738435)
        self.dx = 84.57977183535695
        self.dy = 329.83781695738435
        self.filelist = self.get_files(datadir)
        self.outpath = outpath
        if not os.path.exists(outpath):
            print('create shapefile director: {}'.format(outpath))
            os.mkdir(outpath)

    def __del__(self):
        pass

    def get_files(self,datadir):
        filelist = []
        for root,dirs,files in os.walk(datadir):
            for file in files:
                fn = os.path.join(root,file)
                filelist.append(fn)
        return filelist

    def read_data(self,fn):
        try:
            flag = os.path.basename(fn[-6:-4])  # get busline flag from filename
            with open(fn,'r',encoding='utf-8') as f:
                data = f.read()
            busdata = json.loads(data)
            busline = busdata['response']['resultset']['busline']
            buslinename = busline['name']
            busno = re.findall(r'(.+)\(.*',buslinename)[0]
            busno = busno + flag         
            features = busline['data']['feature']
            return features, busno
        except Exception as e:
            # print(e)
            print('文件{}读取失败!'.format(fn))
            return ('','')

    def parse_to_line(self,fn):
        # parse json to bus line feature
        # # first feature is bus line
        features, busno = self.read_data(fn)
        feat0 = features[0]
        pnts = feat0['Points']['txt'].split(',')
        caption = feat0['caption']
        try:
            stop_match = re.search(r'.+\(((.+)-(.+))\)',caption)
            stop0 = stop_match.group(2)
            stop1 = stop_match.group(3)
            direction = stop_match.group(1)
        except:
            print('{} match error!'.format(fn))
        feat0id = feat0['id']       
        attrlist = [{'busno': busno, 'stop0': stop0, 'stop1': stop1, 'id': feat0id, '往返方向':direction}]
        geomlist = "LINESTRING( "
        for i in range(0,len(pnts)-1,2):
            # x,y = pnts[i], pnts[i+1]
            # x = str(float(x[:-2])*10000000.0)
            # shift x,y
            x,y = pnts[i], pnts[i+1]
            x = str(float(x[:-2])*10000000.0+self.dx)
            y = str(float(y)+self.dy)
            geomlist += x + ' ' + y + ','
        geomlist = [geomlist[:-1] + ')']
        return (geomlist, attrlist)

    def parse_to_stop(self,fn):
        # parse json to bus stops feature
        features, busno = self.read_data(fn)
        geomlist = []
        attrlist = []
        for feat in features[1:]:
            attr = {}
            x,y = feat['Points']['txt'].split(',')
            # x = str(float(x[:-2])*10000000.0)
            # shift x,y
            x = str(float(x[:-2])*10000000.0 + self.dx)
            y = str(float(y) + self.dy)
            geomlist.append("POINT (" + x + " " + y + ")")
            attr['busno'] = busno
            attr['id'] = feat['id']
            attr['stoporder'] = feat['stoporder']
            attr['stopname'] = feat['caption']
            attrlist.append(attr)

        return (geomlist, attrlist)

    def merge_to_layer(self,featuretype):
        # merge bus line or stops to one layer
        spatialref = osr.SpatialReference()
        geomlist = []
        attrlist = []
        if featuretype == 'line':
            geomtype = ogr.wkbLineString
            fieldlist = [{'type': ogr.OFTString, 'name': 'busno'}, {'type': ogr.OFTString, 'name': 'stop0'},\
                        {'type': ogr.OFTString, 'name': 'stop1'}, {'type': ogr.OFTString, 'name': 'id'},\
                        {'type': ogr.OFTString, 'name': '往返方向'}]
            for fn in self.filelist:
                try:            
                    geom,attr = self.parse_to_line(fn)            
                except Exception as e:
                    # print(e)
                    print('parse line data error. file:{}'.format(fn))
                    continue
                geomlist += geom
                attrlist += attr
        if featuretype == 'stops':
            geomtype = ogr.wkbPoint            
            fieldlist = [{'type': ogr.OFTString, 'name': 'busno'}, {'type': ogr.OFTString, 'name': 'id'},\
                        {'type': ogr.OFTInteger, 'name': 'stoporder'}, {'type': ogr.OFTString, 'name': 'stopname'}]
            for fn in self.filelist:
                try:          
                    geom,attr = self.parse_to_stop(fn)
                except:
                    print('parse stops data error. file:{}'.format(fn))
                    continue
                geomlist += geom
                attrlist += attr            

        return (spatialref, geomtype, fieldlist, geomlist, attrlist)

    def run(self):
        linedata = self.merge_to_layer('line')
        stopdata = self.merge_to_layer('stops')
        outfn_stop =  self.outpath + "\\bjbus_stops.shp"
        outfn_line = self.outpath + "\\bjbus_lines.shp"
        shp = Shape()
        shp.write(outfn_line,linedata)
        shp.write(outfn_stop,stopdata)


if __name__ == '__main__':
    # 往
    # json_path = r"C:\Users\china\Desktop\busline\beijing_BusData" 
    # shp_outpath = r'C:\Users\china\Desktop\busline\beijingBusLineShp'
    # 返
    json_path = r"C:\Users\china\Desktop\busline\busdata_come" 
    shp_outpath = r'C:\Users\china\Desktop\busline\bj_busline_come'

    # download bus data
    # t1 = time.perf_counter()
    # busdata = BusData(json_path)
    # flag = '1'    # 0往 1返
    # busdata.run(flag)
    # t2 = time.perf_counter()
    # print('spider run time:{:.2f}s'.format(t2-t1))
    # del busdata

    # generate bus shape file
    # test = BusLineShp(json_path,shp_outpath)
    # test.run()
    print('ok')
