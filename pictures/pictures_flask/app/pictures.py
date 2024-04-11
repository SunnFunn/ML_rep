import numpy as np
import time
import base64
import io
import fitz

import PIL
from PIL import Image, ImageChops, ImageOps, ImageDraw, ImageFilter, ImageFont, ImageEnhance

Image.MAX_IMAGE_PIXELS = ---------------

import tempfile
import shutil
import os
from pathlib import Path
import base64
import glob
import io
import itertools
from itertools import product
import torch
import cv2

from app.text import text_comparison, page_size, drawings_number
from app.model_ae import transform_encoder, model_encoder

model_encoder.load_state_dict(torch.load(--------------------------, map_location=torch.device('cpu')))
cv2.setUseOptimized(True)

# функция разделения pdf файлов на отдельные страницы для послеующего их сравнения
def partitioning(file1_path, file2_path, DIRNAME1, DIRNAME2):
    
    return paths1, paths2


# функция конвертации jpeg файла в pdf файл
def jpg_to_pdf(filepath, doc):
    
    return doc


# функция расчета коэффициента перекрытия боксов
def iou(bboxes_tuple):
    return iou


# функция поиска областей картинки с разным содержанием
def find_nonsimilarities(im1, im2, area_lower_limit=10, area_upper_limit=1000,
                         threshold=0, kernel=(2, 2), iterations=1,
                         transform=None, model=None, distance_thresh=0.9,
                         im_filter1 = ImageFilter.EDGE_ENHANCE, im_filter2 = ImageFilter.BLUR):
    

    return coords_new


# функция сравнения картинок и сохранения картинки с выделенными в боксы разностными областями
def get_pictures_blend(im1, im2, bboxes1, bboxes2, page_size1, page_size2, draws, page_number1, page_number2,
                       distance_thresh, kernel, iterations, im_filter1, im_filter2, blend_level, path1, path2):
    ..............................
.....................................
        background1_draw.text((10, 50),
                              text=f'Страница номер: {page_number1 + 1}, сравнивалась со страницей {page_number2 + 1} во втором документе',
                              fill=(255, 0, 0), font=myFont2)
        background2_draw.text((10, 50),
                              text=f'Страница номер: {page_number2 + 1}, сравнивалась со страницей {page_number1 + 1} в первом документе',
                              fill=(255, 0, 0), font=myFont2)
        result1 = Image.blend(background1, im1, blend_level)
        result2 = Image.blend(background2, im2, blend_level)

        result1.save(path1, optimize=True, quality=15)
        result2.save(path2, optimize=True, quality=15)

    else:
        pass

#основная функция сравнения страниц
def compare(inputs_list):
    .......................
.....................................

    get_pictures_blend(im1, im2, b1, b2, page_size1, page_size2, draws, page_number1, page_number2,
                       inputs_list[4], inputs_list[5], inputs_list[6], ImageFilter.EDGE_ENHANCE, inputs_list[7],
                       inputs_list[8], path1_jpg, path2_jpg)

#функция конвертации jpeg в pdf и объединения отдельных страниц в единый pdf документ
def join_jpeg(inputs_list, path1, path2):
    doc1 = fitz.open()
    doc2 = fitz.open()
   ..........................................
.............................................
        doc1.save(path1)
        doc2.save(path2)
