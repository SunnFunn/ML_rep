import numpy as np
import streamlit as st

import PIL
from PIL import Image, ImageChops, ImageOps
from pdf2image import convert_from_path, convert_from_bytes

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
             '2':'Разрешенные форматы: jpg, jpeg, png',
             '3':'Нажмите кнопку сравнения картинок',
             '4':'Посмотрите на результат',
             '5':'Разности выделены красным цветом'
}

#выводим справочную информацию она боковую панель
st.sidebar.markdown('**Для анализа разности картинок выполните следующие шаги:**')
for key,value in reference.items():
    st.sidebar.markdown(f'**{key}**: {value}')

img_file_buffer_1 = st.file_uploader("Загрузите первую картинку")
img_file_buffer_2 = st.file_uploader("Загрузите вторую картинку")

if img_file_buffer_1 and img_file_buffer_2 is not None:
	
    im_1 = Image.open(img_file_buffer_1)
    im_2 = Image.open(img_file_buffer_2)
else:
	st.write('## **Вы не загрузили одну или обе картинки!**')

FILTER_THRESHOLD = st.slider('Укажите порог фильтрации шума в разностной кртинке', 0, 255, 200)
st.write("Порог фильтрации:", FILTER_THRESHOLD)

#функция поиска разницы в картинках
def get_pictures_difference(im_1, im_2):
	
	#находим разностную картинку
	diff = ImageChops.difference(im_1, im_2)
	
	#инвертируем разностную картинку
	diff_inv = ImageOps.invert(diff)
	
	#перекрасим ее в монохромный красный цвет
	red, green, blue = diff_inv.split()
	mask_red = red.point(lambda i: i*2 if i < FILTER_THRESHOLD else i)
	mask_green = green.point(lambda i: 0 if i < FILTER_THRESHOLD else 255)
	mask_blue = blue.point(lambda i: 0 if i < FILTER_THRESHOLD else 255)
	diff_inv_red = Image.merge('RGB', [mask_red, mask_green, mask_blue])
		
	return diff_inv_red

def get_pictures_blend(diff_inv_red, im_2):

	result = Image.blend(im_2, diff_inv_red, 0.8)
	return result

#делаем кнопку запуска блока расчета прогноза и под нее заводим сам расчет прогноза
result = st.button('Получите сравнительную картинку')
if result:
	diff_inv_red = get_pictures_difference(im_1, im_2)
	result = get_pictures_blend(diff_inv_red, im_2)
	
	#сохраняем результат
	result.save('output/result.jpg')
	
	st.image(result,
	caption='На этой картинке красным цветом выделена разница между сравниваемыми картинками'
	)
	
#скачиваем картинку
with open("output/result.jpg", "rb") as file:
    btn = st.download_button(
            label="Скачайте картинку",
            data=file,
            file_name="result.jpg",
            mime="image/png"
          )
	
exit_app = st.sidebar.button("Shut Down")
if exit_app:
    # Give a bit of delay for user experience
    time.sleep(2)
    # Close streamlit browser tab
    keyboard.press_and_release('ctrl+w')
    # Terminate streamlit python process
    pid = os.getpid()
    p = psutil.Process(pid)
    p.terminate()
