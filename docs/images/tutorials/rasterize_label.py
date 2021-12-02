
from osgeo import gdal, gdal_array, ogr
import mygrid as cropfarm

fn_ras = '2019_9_4_res.tif'
fn_vec = 'esribbb.shp'
output = "lab_all_values.tif"

ras_ds = gdal.Open(fn_ras)
vec_ds = ogr.Open(fn_vec)

lyr = vec_ds.GetLayer()
geot = ras_ds.GetGeoTransform()
proj = ras_ds.GetProjection()

drv_tiff = gdal.GetDriverByName("GTiff")
chn_ras_ds = drv_tiff.Create(output, ras_ds.RasterXSize, ras_ds.RasterYSize, 1, gdal.GDT_Byte)
chn_ras_ds.SetGeoTransform(geot)

gdal.RasterizeLayer(chn_ras_ds, [1], lyr, options=['ATTRIBUTE=fid'])
chn_ras_ds.GetRasterBand(1).SetNoDataValue(0.0) # Change No Data Value to 0
chn_ras_ds.SetProjection (proj) # Set Projection as the source
chn_ras_ds = None

#change all values >= 1 to 1
final_output = "final_lab.tif"

ds = gdal.Open(output)
b1 = ds.GetRasterBand(1)
arr = b1.ReadAsArray()

data = (arr >= 1)
gdal_array.SaveArray(data.astype("byte"), final_output, "GTIFF", ds)
data = None

cropfarm.mygridfun(fn_ras, ".jpg","DataSet\image\image" ) #Sat_Raster
cropfarm.mygridfun(final_output, ".png", "DataSet\label\label" ) #label_raster