import numpy as np
import streamlit as st

import PIL
from PIL import Image, ImageChops, ImageOps
from pdf2image import convert_from_path, convert_from_bytes

import tempfile
from pathlib import Path

import time
import keyboard
import os
import psutil

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

#функция поиска разницы в картинках
def get_pictures_difference(im_1, im_2, FILTER_THRESHOLD):
	
	FILTER_THRESHOLD = st.slider('Укажите порог фильтрации шума в разностной кртинке', 0, 255, FILTER_THRESHOLD)
	st.write("Порог фильтрации:", FILTER_THRESHOLD)
	
	#находим разностную картинку
	diff = []
	for page_1, page_2 in zip(im_1,im_2):
		diff.append(ImageChops.difference(page_1, page_2))
	
	#инвертируем разностную картинку
	diff_inv = []
	for image in diff:
		diff_inv.append(ImageOps.invert(image))
	
	#перекрасим ее в монохромный красный цвет
	diff_inv_red = []
	for image in diff_inv:
		diff_inv_numpy = np.array(image)
		diff_inv_numpy[:,:,0][diff_inv_numpy[:,:,0] < FILTER_THRESHOLD] = 255
		diff_inv_numpy[:,:,1][diff_inv_numpy[:,:,1] < FILTER_THRESHOLD] = 0
		diff_inv_numpy[:,:,2][diff_inv_numpy[:,:,2] < FILTER_THRESHOLD] = 0
		diff_inv_red.append(Image.fromarray(diff_inv_numpy, 'RGB'))
	
	return diff_inv_red

def get_pictures_blend(diff_inv_red, im_2):
	result = []
	for image_1, image_2 in zip(diff_inv_red,im_2):
		result.append(Image.blend(image_1, image_2, 0.2))
	
	return result

#скачиваем картинки
def load_pictures(im_1):
	for im in im_1:
		with open(f"app/output/result_{im_1.index(im)}.jpg", "rb") as file:
			btn = st.download_button(
			label=f"Скачайте сравнительну картинку {im_1.index(im)+1}",
			data=file,
			file_name="result.jpg",
			mime="image/png"
			)

def main(file_option, FILTER_THRESHOLD):
	if file_option == 'pdf':
		file_1 = st.file_uploader("Выберите ваш первый файл", type="pdf")
		file_2 = st.file_uploader("Выберите ваш второй файл", type="pdf")
	else:
		file_1 = st.file_uploader("Выберите ваш первый файл")
		file_2 = st.file_uploader("Выберите ваш второй файл")
	st.write('Загрузите картинки')
	if file_1 and file_2 is not None:
		if file_option == 'pdf':
			im_1, im_2 = pdf_converter(file_1, file_2)
		else:
			im_1, im_2 = img_converter(file_1, file_2)
		diff_inv_red = get_pictures_difference(im_1, im_2, FILTER_THRESHOLD)
		result =  get_pictures_blend(diff_inv_red, im_2)
		result_button = st.button('Посмотрите сравнительные картинки')
		if result_button:
			for im in result:
				im.save(f'app/output/result_{result.index(im)}.jpg')
				st.image(im, caption='На этой картинке красным цветом выделена разница между сравниваемыми картинками')
			load_pictures(im_1)

#выход из приложения
def exit_app():
	exit_app_button = st.sidebar.button("Закрыть приложение")
	if exit_app_button:
		# Give a bit of delay for user experience
		time.sleep(2)
		# Close streamlit browser tab
		keyboard.press_and_release('ctrl+w')
		# Terminate streamlit python process
		pid = os.getpid()
		p = psutil.Process(pid)
		p.terminate()
