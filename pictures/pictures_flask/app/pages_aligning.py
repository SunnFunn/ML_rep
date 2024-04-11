import fitz
import difflib as dl
import os
import numpy as np
import multiprocessing as mp
from skimage.metrics import structural_similarity

import PIL
from PIL import Image

from app.text import drawings_number

#функция измерения расстояния между текстами страниц
def pages_distance(pdf_file_path):
		
	return dist

#функция поиска лишних страниц в сравниваемых документах и их удаление из списков путей к страницам
def pages_align(page_nums1, page_nums2, paths1, paths2):

	
	return extra_pages1, extra_pages2, page_numbers1_final, page_numbers2_final
