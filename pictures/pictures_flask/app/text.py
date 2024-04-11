import fitz
import difflib as dl

import numpy as np
import re

#функция определения размера страницы
def page_size(path1):
	pdf = fitz.open(path1)
	w = pdf[0].mediabox.width
	h = pdf[0].mediabox.height
	return (w,h)

# функция подсчета количества графических элементов на странице
def drawings_number(path1):
	pdf = fitz.open(path1)
	return len(pdf[0].get_drawings())

#функция сравнения страниц с текстом и поиска координат bbox для разностных слов
def text_comparison(path1, path2):
	#открываем pdf страницы
	doc1 = fitz.open(path1)
	doc2 = fitz.open(path2)
	
	.....................
...................................		
			
	return bboxes1, bboxes2
