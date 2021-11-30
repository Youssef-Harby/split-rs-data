# Creating tools to handle raster and vector data to split it into small pieces equaled in size for machine learning datasets

- [X] Creating Docker Image for development env.
- [x] Splitting raster data into equal pieces with [rasterio](https://github.com/rasterio/rasterio) (512×512) thanks to [@geoyee](https://github.com/geoyee).
- [x] Splitting raster data into equal pieces with [GDAL](https://github.com/OSGeo/gdal) , https://gdal.org/.
- [x] Rasterize shapefile to raster in the same satellite pixel size and projection.
- [X] Convert 24 or 16 bit raster to 8 bit.
- [X] Export as jpg (for raster) and png (for rasterized shapefile) with GDAL.
- [ ] Validation of training and testing datasets for paddlepaddle,YOLO-COCO .. etc.
- [ ] Simplify multi-polygons with GDAL/OGR or any other method.
- [ ] GUI

 ![](/docs/images/vQ9YMn.gif)
