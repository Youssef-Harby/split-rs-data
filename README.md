[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Youssef-Harby/split-rs-data/main?labpath=Tutorial.ipynb)
[![CodeFactor](https://www.codefactor.io/repository/github/youssef-harby/split-rs-data/badge)](https://www.codefactor.io/repository/github/youssef-harby/split-rs-data)


# Creating tools to handle raster and vector data to split it into small pieces equaled in size for machine learning datasets

## How To Use

- Install docker https://docs.docker.com/engine/install/ (macos, Windows or Linux)

- Clone the Repository : 
  
  `git clone https://github.com/Youssef-Harby/split-rs-data.git`

- Go to project directory :
  
   `cd split-rs-data`

- Copy and paste your raster(.tif) and vector(.shp) files into a seperated folders :

- ```
  
  ./split-rs-data/DataSet/  # Dataset root directory
  |--raster  # Original raster data
  |  |--xxx1.tif (xx1.png)
  |  |--...
  |  └--...
  |
  |--vector # All shapefiles in the same place (.shx, .shp..etc)
  |  |--xxx1.shp
  |  |--xxx1.shx / .prj  / .cpg / .dbf ....
  |  └--xxx2.shp
  ```

- Build the docke image : ```docker compose up --build ```

- go to http://127.0.0.1:8888/

- you will find your token in the cli of the image.
  
  ![](https://github.com/Youssef-Harby/Remote-sensing-building-extraction-to-3D-model-using-Paddle-and-Grasshopper/blob/main/md_images/jnb-token.png?raw=true)

- Open Tutorial.ipynb to learn

- Or define your vector and raster folders in multi_raster_vector.py file and run it in docker by open cli and type :
  
  `python multi_raster_vector.py`

## TODO

- [x] Creating Docker Image for development env.
- [x] Splitting raster data into equal pieces with [rasterio](https://github.com/rasterio/rasterio) (512×512) thanks to [@geoyee](https://github.com/geoyee).
- [x] Splitting raster data into equal pieces with [GDAL](https://github.com/OSGeo/gdal) , https://gdal.org/.
- [x] Rasterize shapefile to raster in the same satellite pixel size and projection.
- [x] Convert 24 or 16 bit raster to 8 bit.
- [x] Export as jpg (for raster) and png (for rasterized shapefile) with GDAL.
- [X] Validation of training and testing datasets for paddlepaddle.
- [ ] GUI
- [X] QGIS Plugin ➡️ [Deep Learning Datasets Maker](https://github.com/deepbands/deep-learning-datasets-maker/)

 ![](/docs/images/vQ9YMn.gif)



## Code In Detail ⬇️



## First - Prepareing Datasets

# 1.Convert Vector to Raster (Rasterize) with reference coordinate system from raster tiff

all these tools made for prepare data for paddlepaddlea.

```python
from osgeo import gdal, ogr
```

- fn\_ras = Input raster data (GTiff)
- fn\_vec = input vector data (Shapefile)

```python
fn_ras = 'DataSet/raster/01/01.tif'
fn_vec = 'DataSet/vector/01/01.shp'
output = 'DataSet/results/lab_all_values.tif'
```

import the GDAL driver "ESRI Shapefile" to open the shapefile


```python
driver = ogr.GetDriverByName("ESRI Shapefile")
```

open raster and shapefile datasets with (shapefile , 1)

- (shapefile , 1) read and write in the shapefile
- (shapefile , 0) read onle the shapefile

```python
ras_ds = gdal.Open(fn_ras)
vec_ds = driver.Open(fn_vec, 1)
```

Get the :

- GetLayer (Only shapefiles have one lyrs other fomates maybe have
  multi-lyrs) \#VECTOR
- GetGeoTransform \#FROM RASTER
- GetProjection \#FROM RASTER

```python
lyr = vec_ds.GetLayer()
geot = ras_ds.GetGeoTransform()
proj = ras_ds.GetProjection() # Get the projection from original tiff (fn_ras)
geot
```

    (342940.8074133941,
     0.18114600000000536,
     0.0,
     3325329.401211367,
     0.0,
     -0.1811459999999247)

Open the shapefile feature to edit in it


```python
layerdefinition = lyr.GetLayerDefn()
feature = ogr.Feature(layerdefinition)
```

`feature.GetFieldIndex` make you to know the id of a specific field name
you want to read/edit/delete

- Also you can list all fields on the shapefile by :

<!-- end list -->

    schema = []
        for n in range(layerdefinition.GetFieldCount()):
            fdefn = layerdefinition.GetFieldDefn(n)
            schema.append(fdefn.name)

- Then I will delete the field called "MLDS" has been assumed by me

```python
yy = feature.GetFieldIndex("MLDS")
if yy < 0:
    print("MLDS field not found, we will create one for you and make all values to 1")
else:
    lyr.DeleteField(yy)
```

add new field to the shapefile with a default value `"1"` and don't
forget to close feature after the edits

```python
new_field = ogr.FieldDefn("MLDS", ogr.OFTInteger)
lyr.CreateField(new_field)
for feature in lyr:
        feature.SetField("MLDS", 1)
        lyr.SetFeature(feature)
        feature = None
```

Set the projection from original tiff (fn\_ras) to the rasterized tiff

```python
drv_tiff = gdal.GetDriverByName("GTiff")
chn_ras_ds = drv_tiff.Create(
        output, ras_ds.RasterXSize, ras_ds.RasterYSize, 1, gdal.GDT_Byte)
chn_ras_ds.SetGeoTransform(geot)
chn_ras_ds.SetProjection(proj)
chn_ras_ds.FlushCache()
```

```python
gdal.RasterizeLayer(chn_ras_ds, [1], lyr, burn_values=[1], options=["ATTRIBUTE=MLDS"])
chn_ras_ds = None
vec_ds = None
```

DONE


## Second - Splitting raster and rasterized files to small tiles 512×512 depends on your memory


```python
ds = gdal.Open(fn_ras)
gt = ds.GetGeoTransform()
```

get coordinates of upper left corner

```python
xmin = gt[0]
ymax = gt[3]
resx = gt[1]
res_y = gt[5]
resy = abs(res_y)
```

```python
import math
import os.path as osp
```

the tile size i want (may be 256×256 for smaller memory size)


```python
needed_out_x = 512
needed_out_y = 512
```

round up to the nearest int

```python
xnotround = ds.RasterXSize / needed_out_x
xround = math.ceil(xnotround)
ynotround = ds.RasterYSize / needed_out_y
yround = math.ceil(ynotround)

print(xnotround)
print(xround)
print(ynotround)
print(yround)
```

    9.30078125
    10
    5.689453125
    6

pixel to meter - 512×10×0.18

```python
pixtomX = needed_out_x * xround * resx
pixtomy = needed_out_y * yround * resy

print (pixtomX)
print (pixtomy)
```

    927.4675200000274
    556.4805119997686

size of a single tile

```python
xsize = pixtomX / xround
ysize = pixtomy / yround

print (xsize)
print (ysize)
```

    92.74675200000274
    92.74675199996143

create lists of x and y coordinates


```python
xsteps = [xmin + xsize * i for i in range(xround + 1)]
ysteps = [ymax - ysize * i for i in range(yround + 1)]
xsteps
```

    [342940.8074133941,
     343033.5541653941,
     343126.3009173941,
     343219.0476693941,
     343311.7944213941,
     343404.54117339413,
     343497.28792539414,
     343590.03467739414,
     343682.78142939415,
     343775.5281813941,
     343868.2749333941]

set the output path

```python
cdpath = "DataSet/image/"
```

loop over min and max x and y coordinates

```python
for i in range(xround):
    for j in range(yround):
        xmin = xsteps[i]
        xmax = xsteps[i + 1]
        ymax = ysteps[j]
        ymin = ysteps[j + 1]

        # gdal translate to subset the input raster

        gdal.Translate(osp.join(cdpath,  \
                        (str("01") + "-" + str(j) + "-" + str(i) + "." + "jpg")), 
                ds, 
                projWin=(abs(xmin), abs(ymax), abs(xmax), abs(ymin)),
                xRes=resx, 
                yRes=-resy, 
                outputType=gdal.gdalconst.GDT_Byte, 
                format="JPEG")
ds = None
```

### Third - Spilit Custom Dataset and Generate File List

For all data that is not divided into training set, validation set, and
test set, PaddleSeg provides a script to generate segmented data and
generate a file list.

#### Use scripts to randomly split the custom dataset proportionally and generate a file list

The data file structure is as follows:

    ./DataSet/  # Dataset root directory
    |--image  # Original image catalog
    |  |--xxx1.jpg (xx1.png)
    |  |--...
    |  └--...
    |
    |--label  # Annotated image catalog
    |  |--xxx1.png
    |  |--...
    |  └--...

Among them, the corresponding file name can be defined according to
needs.

The commands used are as follows, which supports enabling specific
functions through different Flags.

    python tools/split_dataset_list.py <dataset_root> <images_dir_name> <labels_dir_name> ${FLAGS}

Parameters:

- dataset\_root: Dataset root directory
- images\_dir\_name: Original image catalog
- labels\_dir\_name: Annotated image catalog

FLAGS:

| FLAG            | Meaning                                                                                                                  | Default                                   | Parameter numbers |
| --------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------- | ----------------- |
| \--split        | Dataset segmentation ratio                                                                                               | 0.7 0.3 0                                 | 3                 |
| \--separator    | File list separator                                                                                                      | "                                         | "                 |
| \--format       | Data format of pictures and label sets                                                                                   | "jpg" "png"                               | 2                 |
| \--label\_class | Label category                                                                                                           | '\_\_background\_\_' '\_\_foreground\_\_' | several           |
| \--postfix      | Filter pictures and label sets according to whether the main file name (without extension) contains the specified suffix | "" ""（2 null characters）                  | 2                 |

After running, `train.txt`, `val.txt`, `test.txt` and `labels.txt` will
be generated in the root directory of the dataset.

**Note:** Requirements for generating the file list: either the original
image and the number of annotated images are the same, or there is only
the original image without annotated images. If the dataset lacks
annotated images, a file list without separators and annotated image
paths will be generated.

#### Example

    python tools/split_dataset_list.py <dataset_root> images annotations --split 0.6 0.2 0.2 --format jpg png

## Dataset file organization

- If you need to use a custom dataset for training, it is recommended
  to organize it into the following structure: custom\_dataset |
  |--images | |--image1.jpg | |--image2.jpg | |--... | |--labels |
  |--label1.png | |--label2.png | |--... | |--train.txt | |--val.txt |
  |--test.txt

The contents of train.txt and val.txt are as follows:

    image/image1.jpg label/label1.png
    image/image2.jpg label/label2.png
    ...

Full Docs :
<https://github.com/PaddlePaddle/PaddleSeg/blob/release/2.3/docs/data/custom/data_prepare.md>


```python
import sys
import subprocess
```

```python
theproc = subprocess.Popen([
"python", 
r"C:\Users\Youss\Documents\pp\New folder\split-rs-data\split_dataset_list.py", #Split text py script
r"C:\Users\Youss\Documents\pp\New folder\split-rs-data\DataSet",  # Root DataSet ath
r"C:\Users\Youss\Documents\pp\New folder\split-rs-data\DataSet\image",  #images path
r"C:\Users\Youss\Documents\pp\New folder\split-rs-data\DataSet\label", 
# "--split", 
# "0.6",  # 60% training
# "0.2",  # 20% validating
# "0.2",  # 20% testing
"--format", 
"jpg", 
"png"])
theproc.communicate()
```

    (None, None)


