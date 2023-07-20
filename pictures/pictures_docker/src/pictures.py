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

#пишем зашоловок и оформляем страницу тематической картинкой
#st.title("Поиск разности картинок")
st.markdown("<h1 style='text-align: center; color: darkblue;'>Поиск разности картинок</h1>", unsafe_allow_html=True)

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

#img_file_buffer_1 = st.file_uploader("Загрузите первую картинку")
#img_file_buffer_2 = st.file_uploader("Загрузите вторую картинку")

#if img_file_buffer_1 and img_file_buffer_2 is not None:
	
#    im_1 = Image.open(img_file_buffer_1)
#    im_2 = Image.open(img_file_buffer_2)
#    width, height = im_2.size
#    resize_coeff = 0.5
#    im_1 = im_1.resize((int(width*resize_coeff), int(height*resize_coeff)))
#    im_2 = im_2.resize((int(width*resize_coeff), int(height*resize_coeff)))
#else:
#	st.write('## **Вы не загрузили одну или обе картинки!**')

pdf_file_1 = st.file_uploader("Выберите ваше первый .pdf file", type="pdf")
pdf_file_2 = st.file_uploader("Выберите ваш второй .pdf file", type="pdf")

if pdf_file_1 and pdf_file_2 is not None:
	# Make temp file path from uploaded file
	with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
		fp = Path(tmp_file.name)
		fp.write_bytes(pdf_file_1.getvalue())
		
		im_1 = convert_from_path(tmp_file.name)
		#st.markdown(f"Converted image1 from PDF")
		#st.image(im_1[0])
		
		fp.write_bytes(pdf_file_2.getvalue())
		
		im_2 = convert_from_path(tmp_file.name)
		#st.markdown(f"Converted image2 from PDF")
		#st.image(im_2[0])

FILTER_THRESHOLD = st.slider('Укажите порог фильтрации шума в разностной кртинке', 0, 255, 200)
st.write("Порог фильтрации:", FILTER_THRESHOLD)

#функция поиска разницы в картинках
def get_pictures_difference(im_1, im_2):
	
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

#делаем кнопку запуска блока расчета прогноза и под нее заводим сам расчет прогноза
st.markdown(f"**Всего количество картинок: {len(im_1)}**")
result = st.button('Посмотрите сравнительные картинки')
if result:
	diff_inv_red = get_pictures_difference(im_1, im_2)
	result = get_pictures_blend(diff_inv_red, im_2)
	#result = result.resize((width, height))
	
	#сохраняем апоказываем результат
	for im in result:
		im.save(f'output/result_{result.index(im)}.jpg')
		st.image(im, caption='На этой картинке красным цветом выделена разница между сравниваемыми картинками'
		)
	
#скачиваем картинки
for im in im_1:
	with open(f"output/result_{im_1.index(im)}.jpg", "rb") as file:
		btn = st.download_button(
		label=f"Скачайте сравнительну картинку {im_1.index(im)+1}",
		data=file,
		file_name="result.jpg",
		mime="image/png"
		)
	
exit_app = st.sidebar.button("Закрыть приложение")
if exit_app:
    # Give a bit of delay for user experience
    time.sleep(2)
    # Close streamlit browser tab
    keyboard.press_and_release('ctrl+w')
    # Terminate streamlit python process
    pid = os.getpid()
    p = psutil.Process(pid)
    p.terminate()

#red, green, blue = diff_inv.split()
#mask_red = red.point(lambda i: i*2 if i < FILTER_THRESHOLD else i)
#mask_green = green.point(lambda i: 0 if i < FILTER_THRESHOLD else 255)
#mask_blue = blue.point(lambda i: 0 if i < FILTER_THRESHOLD else 255)
#diff_inv_red = Image.merge('RGB', [mask_red, mask_green, mask_blue])
