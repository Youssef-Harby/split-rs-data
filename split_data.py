import os
import os.path as osp
from typing import Union, Tuple, List, Any
import numpy as np
import cv2
from PIL import Image

import rasterio
from rasterio.windows import Window


def __mkdir_p(path: str, sub_name: str) -> str:
    new_path = osp.join(path, sub_name)
    if not osp.exists(new_path):
        os.makedirs(new_path)
    return new_path


def __get_file_name(path: str) -> str:
    _, full_name = osp.split(path)
    name, _ = osp.splitext(full_name)
    return name


def __full_size(ima: np.array, grid_size: Union[List, Tuple]=(512, 512)) -> np.array:
    h, w = ima.shape[:2]
    if len(ima.shape) == 2:
        img = np.zeros(grid_size, dtype=np.uint16)
        img[:h, :w] = ima
    else:
        img = np.zeros((grid_size[0], grid_size[1], 3), dtype=np.uint16)
        img[:h, :w, :] = ima
    return img.astype("uint8")


def __get_grid(rasterio_data: Any, row: int, col: int, 
               grid_size: Union[List, Tuple]=(512, 512)) -> np.array:
    grid_size = np.array(grid_size)
    grid_idx = np.array([row, col])
    ul = grid_idx * grid_size
    lr = ul + grid_size
    window = Window(ul[1], ul[0], (lr[1] - ul[1]), (lr[0] - ul[0]))
    rgb = []
    count = rasterio_data.meta["count"]
    if count == 1:  # mask
        ima = rasterio_data.read(1, window=window)
        return __full_size(ima, grid_size)
    elif count == 3:  # image
        for b in range(count):
            rgb.append(rasterio_data.read((b + 1), window=window))
        ima = cv2.merge([np.uint16(c) for c in rgb])
        return __full_size(ima, grid_size)
    else:
        raise ValueError("count must be 1 or 3!")


def __save_palette(label, save_path):
    bin_colormap = np.ones((256, 3)) * 255  # color
    bin_colormap[0, :] = [0, 0, 0]
    bin_colormap = bin_colormap.astype(np.uint8)
    visualimg  = Image.fromarray(label, "P")
    palette = bin_colormap
    visualimg.putpalette(palette) 
    visualimg.save(save_path, format='PNG')


def split_tif(img_path: str, 
              lab_path: str, 
              save_folder: str,
              ssize :Union[List, Tuple]=(512, 512)) -> None:
    """ divide the large image to the specified size.

    Args:
        img_path (str): path of image raster.
        lab_path (str): path of mask raster.
        save_folder (str): path of save result folder.
        ssize (Union[List, Tuple], optional): slice size. Defaults to (512, 512).
    """
    img_save_folder = __mkdir_p(save_folder, "Images")
    lab_save_folder = __mkdir_p(save_folder, "Labels")
    print("folder created!")
    name = __get_file_name(img_path)
    img = rasterio.open(img_path)
    lab = rasterio.open(lab_path)
    if img.meta["width"] != lab.meta["width"] and img.meta["height"] != lab.meta["height"]:
        raise ValueError("image's size must equal label's size!")
    img_size = np.array([img.meta["height"], img.meta["width"]])
    grid_count = list(np.ceil(img_size / np.array(ssize)).astype("uint8"))
    for r in range(grid_count[0]):
        for c in range(grid_count[1]):
            name_i = name + "_" + str(r) + "_" + str(c)
            img_i = __get_grid(img, r, c)
            img_save_path = osp.join(img_save_folder, (name_i + ".jpg"))
            cv2.imwrite(img_save_path, cv2.cvtColor(img_i, cv2.COLOR_RGB2BGR))
            lab_i = __get_grid(lab, r, c)
            lab_save_path = osp.join(lab_save_folder, (name_i + ".png"))
            __save_palette(lab_i, lab_save_path)
    print("finished!")


if __name__ == "__main__":
    img_path = r"Raster\2019_9_4_res.tif"
    lab_path = r"Raster\2019_9_4_lab_2.tif"
    save_folder = r"Datasets"
    split_tif(img_path, lab_path, save_folder)