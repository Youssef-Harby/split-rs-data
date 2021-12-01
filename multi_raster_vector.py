import os
import glob
from osgeo import gdal, gdal_array, ogr
import math

rasdir = "DataSet/raster/"
vecdir = "DataSet/vector/"

# raster and vector names
rasterName = [os.path.basename(rr) for rr in glob.glob(
    rasdir + "**/*.tif", recursive=True) + glob.glob(
        rasdir + "**/*.bmp", recursive=True)]
vectorName = [os.path.basename(vv) for vv in glob.glob(
    vecdir + "**/*.shp", recursive=True)]

# raster and vector relative path
rasterList = [os.path.normpath(rr) for rr in glob.glob(
    rasdir + "**/*.tif", recursive=True) + glob.glob(
        rasdir + "**/*.bmp", recursive=True)]
vectorList = [os.path.normpath(vv) for vv in glob.glob(
    vecdir + "**/*.shp", recursive=True)]


def rasterize(fn_ras, fn_vec, vvv):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ras_ds = gdal.Open(fn_ras)
    vec_ds = driver.Open(fn_vec, 1)

    lyr = vec_ds.GetLayer()
    geot = ras_ds.GetGeoTransform()
    proj = ras_ds.GetProjection()  # Get the projection from original tiff (fn_ras)

    layerdefinition = lyr.GetLayerDefn()
    feature = ogr.Feature(layerdefinition)

    schema = []
    for n in range(layerdefinition.GetFieldCount()):
        fdefn = layerdefinition.GetFieldDefn(n)
        schema.append(fdefn.name)
    yy = feature.GetFieldIndex("MLDS")
    if yy < 0:
        print("MLDS field not found, we will create one for you and make all values to 1")
    else:
        lyr.DeleteField(yy)
        #     # lyr.ResetReading()
        # else:
    new_field = ogr.FieldDefn('MLDS', ogr.OFTInteger)
    lyr.CreateField(new_field)
    for feature in lyr:
        feature.SetField("MLDS", 1)
        lyr.SetFeature(feature)
        feature = None

    # isAttributeOn = att_field_input if att_field_input != '' else first_att_field
    # pixelsizeX = 0.2 if ras_ds.RasterXSize < 0.2 else ras_ds.RasterXSize
    # pixelsizeY = -0.2 if ras_ds.RasterYSize < -0.2 else ras_ds.RasterYSize

    drv_tiff = gdal.GetDriverByName("GTiff")
    chn_ras_ds = drv_tiff.Create(
        output, ras_ds.RasterXSize, ras_ds.RasterYSize, 1, gdal.GDT_Byte)
    chn_ras_ds.SetGeoTransform(geot)

    gdal.RasterizeLayer(chn_ras_ds, [1], lyr, options=[
        'ATTRIBUTE=MLDS'])
    # Change No Data Value to 0
    chn_ras_ds.GetRasterBand(1).SetNoDataValue(-9999)
    chn_ras_ds.FlushCache()

    # Set the projection from original tiff (fn_ras) to the rasterized tiff
    chn_ras_ds.SetProjection(proj)
    chn_ras_ds = None
    # lyr.DeleteField(yy) # delete field
    vec_ds = None


def mygridfun(fn_ras, cdpath, frmt_ext, imgfrmat, scaleoptions, needed_out_x, needed_out_y, rrrr):
    ds = gdal.Open(fn_ras)
    gt = ds.GetGeoTransform()

    # get coordinates of upper left corner
    xmin = gt[0]
    ymax = gt[3]
    resx = gt[1]
    res_y = gt[5]
    resy = abs(res_y)

    # round up to nearst int to the
    xnotround = ds.RasterXSize/needed_out_x
    xround = math.ceil(xnotround)
    ynotround = ds.RasterYSize/needed_out_y
    yround = math.ceil(ynotround)

    # pixel to meter - 512×10×0.18
    pixtomX = needed_out_x*xround*resx
    pixtomy = needed_out_y*yround*resy
# size of a single tile
    xsize = pixtomX/xround
    ysize = pixtomy/yround
# create lists of x and y coordinates
    xsteps = [xmin + xsize * i for i in range(xround+1)]
    ysteps = [ymax - ysize * i for i in range(yround+1)]

# loop over min and max x and y coordinates
    for i in range(xround):
        for j in range(yround):
            xmin = xsteps[i]
            xmax = xsteps[i+1]
            ymax = ysteps[j]
            ymin = ysteps[j+1]

            # use gdal warp
            # gdal.WarpOptions(outputType=gdal.gdalconst.GDT_Byte)
            # gdal.Warp("ds"+str(i)+str(j)+".tif", ds,
            # outputBounds = (xmin, ymin, xmax, ymax), dstNodata = -9999)

            # or gdal translate to subset the input raster
            gdal.Translate(cdpath+str(rrrr)+"-"+str(i)+str(j)+'.'+frmt_ext, ds, projWin=(abs(xmin), abs(ymax), abs(xmax), abs(ymin)),
                           xRes=resx, yRes=-resy, outputType=gdal.gdalconst.GDT_Byte, format=imgfrmat, scaleParams=[[scaleoptions]])

            # close the open dataset!!!
            # ds = None


for vvv in range(len(vectorList)):
    fn_ras = rasterList[vvv]
    fn_vec = vectorList[vvv]
    output = "DataSet/rasterized/values/" + vectorName[vvv] + ".tif"
    rasterize(fn_ras, fn_vec, vvv)
    mygridfun(fn_ras, "DataSet/image/image", "jpg", "JPEG", "", 512, 512, vvv)
    mygridfun(output, "DataSet/label/image", "png", "PNG", "", 512, 512, vvv)
