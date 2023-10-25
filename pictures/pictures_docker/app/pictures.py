import numpy as np
import streamlit as st
from PyPDF2 import PdfWriter, PdfReader

#import multiprocessing as mp
import concurrent.futures

import PIL
from PIL import Image, ImageChops, ImageOps, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from pdf2image import convert_from_path, convert_from_bytes

Image.MAX_IMAGE_PIXELS = 1000000000

import cv2

import tempfile
import shutil
import os
from pathlib import Path
import base64
import glob

import torch
from app.model_ae import model_encoder, transform_encoder

model_encoder.load_state_dict(torch.load('./app/models/model_ae_v3_100.pth', map_location=torch.device('cpu')))

def partitioning(file_1, file_2):
	with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
		fp = Path(tmp_file.name)
		fp.write_bytes(file_1.getvalue())
		temp_dir1 = tempfile.mkdtemp()
		
		path1 = []
		pdf1 = PdfReader(open(tmp_file.name, 'rb'))
		
		for i in range(len(pdf1.pages)):
			pdf1_parts = PdfWriter()
			pdf1_parts.add_page(pdf1.pages[i])
			with open(f'{temp_dir1}/pdf1_{i}.pdf', 'wb') as outputStream:
				pdf1_parts.write(outputStream)
				path1.append(f'{temp_dir1}/pdf1_{i}.pdf')
		
		fp.write_bytes(file_2.getvalue())
		temp_dir2 = tempfile.mkdtemp()
		
		path2 = []
		pdf2 = PdfReader(open(tmp_file.name, 'rb'))
		
		for i in range(len(pdf2.pages)):
			pdf2_parts = PdfWriter()
			pdf2_parts.add_page(pdf2.pages[i])
			with open(f'{temp_dir2}/pdf2_{i}.pdf', 'wb') as outputStream:
				pdf2_parts.write(outputStream)
				path2.append(f'{temp_dir2}/pdf2_{i}.pdf')
		
		return path1, path2, temp_dir1, temp_dir2

#функция конвертации pdf файла в png файлы постранично и складывание png файлов в папки временного содержания
def pdf_converter(path1, path2, temp_dir1, temp_dir2, dpi = 200):
	
	path1_out = []
	path2_out = []
	
	for idx, p in enumerate(zip(path1, path2)):
		im_1 = convert_from_path(p[0], dpi=dpi, fmt="jpeg", jpegopt={'quality':60, 'progressive':True, 'optimize':True})
		im_2 = convert_from_path(p[1], dpi=dpi, fmt="jpeg", jpegopt={'quality':60, 'progressive':True, 'optimize':True})
		
		im_1[0].save(f'{temp_dir1}/im1_{idx}.jpg')
		im_2[0].save(f'{temp_dir2}/im2_{idx}.jpg')
		
		os.remove(p[0])
		os.remove(p[1])
		
		path1_out.append(f'im1_{idx}.jpg')
		path2_out.append(f'im2_{idx}.jpg')
	
	return path1_out, path2_out

#функция чтения jpg файлов и складывание их в папки временного содержания
def img_converter(file_1, file_2):
	im_1 = Image.open(file_1)
	temp_dir1 = tempfile.mkdtemp()
	im_1.save(f'{temp_dir1}/page_0.jpg')
	path1 = sorted(os.listdir(f'{temp_dir1}'))
	
	im_2 = Image.open(file_2)
	temp_dir2 = tempfile.mkdtemp()
	im_2.save(f'{temp_dir2}/page_0.jpg')
	path2 = sorted(os.listdir(f'{temp_dir2}'))
	
	return path1, path2, temp_dir1, temp_dir2

#функция поиска областей картинки с разным содержанием
def find_nonsimilarities(im1, im2, area_lower_limit = 10,  area_upper_limit = 1000,
                         threshold = 0, kernel = (2,2), iterations=1,
                         transform = None, model= None, distance_thresh = 0.9,
                         im_filter = ImageFilter.EDGE_ENHANCE):
  #конвертируем картинки в серые картинки
  g1 = im1.convert('L')
  g2 = im2.convert('L')
  #ищем попиксельную разность
  difference = ImageChops.difference(g1, g2)
  
  #конвертируем разностную картинку черно белую, где белым выделены области с разностями
  im = np.array(difference.filter(im_filter))
  ret, thresh = cv2.threshold(im, threshold, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
  
  #размываем области в разными пикселями для формирования сплошных областей под обводку контурами
  rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel)
  dilation = cv2.dilate(thresh, rect_kernel, iterations = iterations)
  
  #находим контуры разностных областей
  contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE,
                                                 cv2.CHAIN_APPROX_NONE)

  #создадим новые пустые списки для заполнения их контурами, прошедшими через фильтры
  # размера площади и уровня иерархии по индексу наличия родителя
  cont_filtered = []
  for idx,cnt in enumerate(contours):
    x,y,w,h = cv2.boundingRect(cnt)
    if cv2.contourArea(cnt) > area_lower_limit and cv2.contourArea(cnt) < area_upper_limit and hierarchy[:, idx, -1][0] == -1:
      cont_filtered.append(cnt)
  
  #создаем список с координатами боксов, внутри которых разностные области
  coords = []
  for cnt in cont_filtered:
    coords.append(cv2.boundingRect(cnt))
  
  coords_new = []
  
  #прогоняем области внутри боксов через энкодер и сравниваем вектора картинок в пространстве признаков
  #сильно близкие вектора отсеиваем, считая их одинаковыми картинками в боксах
  for coord in coords:
	  
	  x,y,w,h = coord
	  diff1 = g1.crop((x,y,x+w,y+h))
	  diff2 = g2.crop((x,y,x+w,y+h))
	  
	  diff1_transformed = transform_encoder(diff1)
	  diff2_transformed = transform_encoder(diff2)
	  
	  with torch.no_grad():
		  emb1 = model.encoder(diff1_transformed.unsqueeze(0))
		  emb2 = model.encoder(diff2_transformed.unsqueeze(0))
		  distance = np.round(torch.nn.functional.cosine_similarity(emb1, emb2, dim=1, eps=1e-8).item(),2)
	  if distance < distance_thresh:
		  coords_new.append(coord)
  return coords_new

#функция сравнения картинок и сохранения картинки с выделенными в боксы разностными областями
def get_pictures_blend(path1_list, path2_list, distance_thresh, kernel, iterations, im_filter,
						dir1 = None, dir2 = None, blend_level=0.2):
	page_numbers = []
	temp_dir_result = tempfile.mkdtemp()
	
	for idx, paths in enumerate(zip(path1_list, path2_list)):
		
		im1 = Image.open(dir1+'/'+paths[0])
		im2 = Image.open(dir2+'/'+paths[1])
		
		pic_size = im1.size
		# Font selection from the downloaded file
		font_size = [30,pic_size[0]//40]
		myFont1 = ImageFont.truetype('./app/fonts/isocpeur.ttf', font_size[0])
		myFont2 = ImageFont.truetype('./app/fonts/isocpeur.ttf', font_size[1])
		
		coords = find_nonsimilarities(im1, im2, area_lower_limit = 400,  area_upper_limit = float('inf'),
									threshold = 200, kernel = kernel, iterations=iterations,
									transform = transform_encoder, model= model_encoder, distance_thresh = distance_thresh,
									im_filter = im_filter)
		if len(coords)>0:
			page_numbers.append(idx)
			
			background = Image.new("RGB", pic_size, (255, 255, 255))
			background_draw = ImageDraw.Draw(background)
		
			for coord_idx, coord in enumerate(coords):			
				x,y,w,h = coord
			
				#background_draw = ImageDraw.Draw(background)
				background_draw.rectangle([(x,y), (x+w,y+h)], fill= None, outline ="red", width=4)
				background_draw.text((x, y-font_size[0]), text = f'Box {len(coords) - coord_idx}, please, check it!', fill =(255, 0, 0),font=myFont1)
		
			background_draw.text((10, 50), text = f'Total number of boxes found: {len(coords)}',
							fill =(255, 0, 0),font=myFont2)
			result = Image.blend(background, im1, blend_level)
			result = result.save(f'{temp_dir_result}/page_{idx}.webp', 'WEBP')
	return page_numbers, temp_dir_result

#функция скачивания картинки
def load_picture(idx, image_path):
	with open(image_path, 'rb') as file:
		bytes = file.read()
		b64 = base64.b64encode(bytes).decode()
		href =  f'<a href="data:file/webp;base64,{b64}" download="page{idx+1}.webp">Скачайте картинку страницы {idx+1}</a>'
	st.markdown(href, unsafe_allow_html=True)

#основная функция, собирающая все шаги сравнительного анализа в единую последовательность
def main(file_option, distance_thresh, dpi, kernel, iterations, im_filter, blend_level):
	st.write('**Загрузите картинки и посмотрите результат их сравнения**')
	
	with st.spinner('Wait for pictures to be compared...'):
		
		#подгружаем файлы	
		file_1 = st.file_uploader("Выберите ваш первый файл", type=file_option)
		file_2 = st.file_uploader("Выберите ваш второй файл", type=file_option)
		if file_1 and file_2 is not None:
			if file_option == 'pdf':
				paths1, paths2, temp_dir1, temp_dir2 = partitioning(file_1, file_2)
				paths1, paths2 = pdf_converter(paths1, paths2, temp_dir1, temp_dir2, dpi)
			else:
				paths1, paths2, temp_dir1, temp_dir2 = img_converter(file_1, file_2)		
			
			#делаем сравнение, если нашли разности, то сохраняем их в папку diffs и далее предлагаем ссылки для скачивания этих картинок
			page_numbers, temp_dir_result =  get_pictures_blend(paths1, paths2, distance_thresh, kernel, iterations, im_filter,
																dir1 = f'{temp_dir1}', dir2 = f'{temp_dir2}', blend_level=blend_level)
			st.write('На картинках красными рамками выделены области с разным содержанием, \
				а в верхнем левом углу указано количество найденных разностей.')
			if not page_numbers:
				st.write('**Картинки идентичны!**')
			else:
				for page in page_numbers:
					im = Image.open(f'{temp_dir_result}/page_{page}.webp')
					st.image(im, caption=f'Страница {page+1}')
					load_picture(page, f'{temp_dir_result}/page_{page}.webp')
			shutil.rmtree(temp_dir1)
			shutil.rmtree(temp_dir2)
			shutil.rmtree(temp_dir_result)
