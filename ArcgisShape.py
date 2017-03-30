from osgeo import gdal, ogr, osr
from osgeo.gdalconst import *
import sys
import os
import numpy as np


class Shape:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def read(self, filepath):
        ds = ogr.Open(filepath, False) # False - read only, True - read/write
        layer = ds.GetLayer(0)
        spatialref = layer.GetSpatialRef() # projection information
        # spatialref.ExportToWkt()
        # spatialref.ExportToProj4()
        lydefn = layer.GetLayerDefn() # layer definition info
        geomtype = lydefn.GetGeomType() # geometry type（wkbPoint, wkbLineString, wkbPolygon）
        fieldlist = [] # field list （type: OFTInteger, OFTReal, OFTString, OFTDateTime
        for i in range(lydefn.GetFieldCount()):
            fddefn = lydefn.GetFieldDefn(i)
            fddict = {'name':fddefn.GetName(),'type':fddefn.GetType(),\
            'width':fddefn.GetWidth(),'decimal':fddefn.GetPrecision()}
            fieldlist += [fddict]
        geomlist, reclist = [], [] # data record – geometry and its attributes
        feature = layer.GetNextFeature() # get feature
        while feature is not None:
            geom = feature.GetGeometryRef()
            geomlist += [geom.ExportToWkt()]
            rec = {}
            for fd in fieldlist:
                rec[fd['name']] = feature.GetField(fd['name'])
            reclist += [rec]
            feature = layer.GetNextFeature()
        ds.Destroy()

        return (spatialref, geomtype, fieldlist, geomlist, reclist)

    def write(self, outfilepath, data):
        spatialref, geomtype, fieldlist, geomlist, reclist = data
        gdal.SetConfigOption('GDAL_FILENAME_IS_UTF8', 'NO') # handle chinese path
        gdal.SetConfigOption('SHAPE_ENCODING', 'gb2312') # 解决 SHAPE 文件的属性值

        driver = ogr.GetDriverByName("ESRI Shapefile")
        if os.access(outfilepath, os.F_OK ): # delete file if exists
            driver.DeleteDataSource(outfilepath)
        ds = driver.CreateDataSource(outfilepath) 
        # spatialref = osr.SpatialReference( 'LOCAL_CS["arbitrary"]' )
        # spatialref = osr.SpatialReference()
        # spatialref.ImportFromProj4('+proj=tmerc ...')
        # spatialref.ImportFromEPSG(3857)

        # create layer
        layer = ds.CreateLayer(outfilepath[:-4], srs=spatialref, geom_type=geomtype)
        # write field list into layer
        for fd in fieldlist:
            field = ogr.FieldDefn(fd['name'],fd['type'])
            if 'width' in fd:
                field.SetWidth(fd['width'])
            if 'decimal' in fd:
                field.SetPrecision(fd['decimal']) 
            layer.CreateField(field)
        # write geometry object and its attributes into layer
        for i in range(len(reclist)):
            geom = ogr.CreateGeometryFromWkt(geomlist[i])
            feat = ogr.Feature(layer.GetLayerDefn()) # create feature
            feat.SetGeometry(geom)
            for fd in fieldlist:
                feat.SetField(fd['name'], reclist[i][fd['name']])
            layer.CreateFeature(feat) # write feature into layer
        ds.Destroy()
 

if __name__ == '__main__':

    # shape
    filepath = r"D:\data\gisdata\ospy_data1\sites.shp"
    
    # test = Shape()
    # data = test.read(filepath)
    # print(data[4])
    # print('='*50)
    # print(data[2])
    # print(len(data[2]))
    # output_filepath = "outshp.shp"
    # test.write(output_filepath,data)
    # sr = osr.SpatialReference()
    # sr.ImportFromEPSG(4326)
    # print(type(sr.ExportToWkt()))
   