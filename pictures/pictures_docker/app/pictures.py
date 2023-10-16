import numpy as np
import streamlit as st

import PIL
from PIL import Image, ImageChops, ImageOps, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from pdf2image import convert_from_path, convert_from_bytes

import cv2

import tempfile
from pathlib import Path

import torch
from app.model_ae import model_encoder, transform_encoder

model_encoder.load_state_dict(torch.load('./app/models/model_ae_v2.pth', map_location=torch.device('cpu')))

# Font selection from the downloaded file
font_size = 20
myFont = ImageFont.truetype('./app/fonts/isocpeur.ttf', font_size)

def sidebar():
	#делаем короткую инструкцию
	reference = {'0': 'Загрузите первую картинку',
				'1':'Загрузите сторую картинку',
				'2':'Разрешенные форматы: pdf',
				'3':'Нажмите кнопку сравнения картинок',
				'4':'Посмотрите на результат',
				'5':'Разности выделены красным цветом',
				'6': 'Скачайте картинку'
					}

	#выводим справочную информацию она боковую панель
	st.sidebar.markdown('**Для анализа разности картинок выполните следующие шаги:**')
	for key,value in reference.items():
		st.sidebar.markdown(f'**{key}**: {value}')

def pdf_converter(file_1, file_2):
	with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
		fp = Path(tmp_file.name)
		fp.write_bytes(file_1.getvalue())
		im_1 = convert_from_path(tmp_file.name)
		
		fp.write_bytes(file_2.getvalue())
		im_2 = convert_from_path(tmp_file.name)
		
		return im_1, im_2

def img_converter(file_1, file_2):
	im_1 = []
	im_1.append(Image.open(file_1))
	im_2 = []
	im_2.append(Image.open(file_2))
	
	return im_1, im_2

#функция поиска областей картинки с разным содержанием
def find_nonsimilarities(im1, im2, area_lower_limit = 10,  area_upper_limit = 1000,
                         threshold = 0, kernel = (2,2), iterations=1,
                         transform = None, model= None, distance_thresh = 0.9):

  im1_numpy = np.array(im1)
  im2_numpy = np.array(im2)

  gray1 = cv2.cvtColor(im1_numpy, cv2.COLOR_BGR2GRAY)
  gray2 = cv2.cvtColor(im2_numpy, cv2.COLOR_BGR2GRAY)
  
  g1 = Image.fromarray(gray1.astype('uint8'), 'L')
  g2 = Image.fromarray(gray2.astype('uint8'), 'L')
  difference = ImageChops.difference(g1, g2)

  im = np.array(difference.filter(ImageFilter.EDGE_ENHANCE_MORE))
  ret, thresh = cv2.threshold(im, threshold, 255, cv2.THRESH_BINARY)

  rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel)
  dilation = cv2.dilate(thresh, rect_kernel, iterations = iterations)

  contours, hierarchy = cv2.findContours(dilation, cv2.RETR_CCOMP,
                                                 cv2.CHAIN_APPROX_NONE)

  #создадим новые пустые списки для заполнения их контурами, прошедшими через фильтры
  # размера площади и уровня иерархии по индексуналичия родителя
  cont_filtered = []
  for idx,cnt in enumerate(contours):
    x,y,w,h = cv2.boundingRect(cnt)
    if cv2.contourArea(cnt) > area_lower_limit and cv2.contourArea(cnt) < area_upper_limit and hierarchy[0][idx][3] == -1:
      cont_filtered.append(cnt)

  coords = []
  for cnt in cont_filtered:
    coords.append(cv2.boundingRect(cnt))

  #вырежем картинки с найденными разностями
  im1_copy = im1_numpy.copy()
  im2_copy = im2_numpy.copy()
  
  coords_new = []

  for coord in coords:
    x,y,w,h = coord
    diff1 = im1_copy[y:y+h, x:x+w]
    diff2 = im2_copy[y:y+h, x:x+w]

    diff1_gray = cv2.cvtColor(diff1, cv2.COLOR_BGR2GRAY)
    diff2_gray = cv2.cvtColor(diff2, cv2.COLOR_BGR2GRAY)
    diff1_im = Image.fromarray(diff1_gray.astype('uint8'), 'L')
    diff2_im = Image.fromarray(diff2_gray.astype('uint8'), 'L')

    diff1_transformed = transform(diff1_im)
    diff2_transformed = transform(diff2_im)
    emb1 = model.encoder(diff1_transformed.unsqueeze(0))
    emb2 = model.encoder(diff2_transformed.unsqueeze(0))
    distance = np.round(torch.nn.functional.cosine_similarity(emb1, emb2, dim=1, eps=1e-8).item(),2)

    if distance < distance_thresh:
      coords_new.append(coord)

  return coords_new

def get_pictures_blend(im_1, im_2):
	result = []
	for idx, images in enumerate(zip(im_1, im_2)):
		
		coords = find_nonsimilarities(images[0], images[1], area_lower_limit = 400,  area_upper_limit = float('inf'),
									threshold = 200, kernel = (20,5), iterations=2,
									transform = transform_encoder, model= model_encoder, distance_thresh = 0.915)
		
		background = Image.new("RGB", images[1].size, (255, 255, 255))
		
		for idx, coord in enumerate(coords):			
			x,y,w,h = coord
			#patch = images[0].crop((x, y, x + w, y + h))
			#patch = patch.resize((w,h))
			#background.paste(patch, (x, y, x + w, y + h))
			
			background_draw = ImageDraw.Draw(background)
			background_draw.rectangle([(x,y), (x+w,y+h)], fill= None, outline ="red", width=2)
			background_draw.text((x, y-font_size), text = f'Box {len(coords) - idx}, please, check it!', fill =(255, 0, 0),font=myFont)
		
		background_draw.text((10, 10), text = f'Total number of boxes found: {len(coords)}',
							fill =(255, 0, 0),font=myFont)
		result.append(Image.blend(background, images[0], 0.2))		
		
	return result

#скачиваем картинки
def load_picture(idx, image):
	with tempfile.TemporaryDirectory() as tmpdirname:
		image.save(f'{tmpdirname}/result{idx}.jpg')
		with open(f'{tmpdirname}/result{idx}.jpg', "rb") as file:
			btn = st.download_button(
			label=f"Скачайте сравнительну картинку {idx+1}",
			data=file,
			file_name="result.jpg",
			mime="image/png"
			)

def main(file_option):
	file_1 = st.file_uploader("Выберите ваш первый файл", type=file_option)
	file_2 = st.file_uploader("Выберите ваш второй файл", type=file_option)
	st.write('Загрузите картинки')
	if file_1 and file_2 is not None:
		if file_option == 'pdf':
			im_1, im_2 = pdf_converter(file_1, file_2)
		else:
			im_1, im_2 = img_converter(file_1, file_2)
		result =  get_pictures_blend(im_1, im_2)
		result_button = st.button('Посмотрите сравнительные картинки')
		if result_button:
			for idx, im in enumerate(result):
				st.image(im, caption='На картинке красными рамками выделены области с разным содержанием, \
				а верхнем левом углу указано количество найденных разностей.')
				load_picture(idx, im)
