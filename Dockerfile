FROM python:3.8.12-slim-bullseye
LABEL maintainer="youssef_harby@yahoo.com"

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .

RUN apt-get update \
  && apt-get install -y libgomp1 \
    ffmpeg libsm6 libxext6 \
    git \
    build-essential \
    gdal-bin libgdal-dev 
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN pip install git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI