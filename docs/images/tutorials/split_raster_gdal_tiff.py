from osgeo import gdal
import math

ds = gdal.Open("2019_9_4_res.tif")
gt = ds.GetGeoTransform()

needed_out_x = 512
needed_out_y = 512

# get coordinates of upper left corner
xmin = gt[0]
ymax = gt[3]
resx = gt[1]
res_y = gt[5]
resy = abs(res_y)

# determine total length of raster
xlen = resx * ds.RasterXSize
ylen = resy * ds.RasterYSize

# overall raster dim in pixels before the edits
img_width =  ds.RasterXSize
img_height = ds.RasterYSize

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
        
        # print("xmin: "+str(xmin))
        # print("xmax: "+str(xmax))
        # print("ymin: "+str(ymin))
        # print("ymax: "+str(ymax))
        # print("\n")
        
        # use gdal warp
        gdal.Warp("ds"+str(i)+str(j)+".tif", ds, 
                  outputBounds = (xmin, ymin, xmax, ymax), dstNodata = -9999)
        # or gdal translate to subset the input raster
        # gdal.Translate("dem_translate"+str(i)+str(j)+".tif", dem, projWin = (xmin, ymax, xmax, ymin), xRes = res, yRes = -res)
 
# close the open dataset!!!
dem = None