import numpy as np
import streamlit as st

import PIL
from PIL import Image
#ImageChops, ImageOps
from pdf2image import convert_from_path, convert_from_bytes

import time
import keyboard
import os
import psutil

#пишем зашоловок и оформляем страницу тематической картинкой
#st.title("Поиск разности картинок")
st.markdown("<h1 style='text-align: center; color: darkblue;'>Поиск разности картинок</h1>", unsafe_allow_html=True)
#st.image('https://phonoteka.org/uploads/posts/2021-07/1625276238_23-phonoteka-org-p-oboi-na-rabochii-stol-chertezhi-oboi-krasi-23.png')

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

#img_file_buffer_1 = st.file_uploader("Загрузите первую картинку", type="pdf")
#img_file_buffer_2 = st.file_uploader("Загрузите вторую картинку", type="pdf")

path1 = st.text_input('Введите путь к первой картинке')
path2 = st.text_input('Введите путь ко второй картинке')

if path1 and path2 is not None:
	
    #im_1 = Image.open(img_file_buffer_1)
    #im_2 = Image.open(img_file_buffer_2)
    im_1 = convert_from_path(path1)[2]
    im_2 = convert_from_path(path2)[2]
else:
	st.write('## **Вы не загрузили одну или обе картинки!**')

FILTER_THRESHOLD = int(st.number_input('Укажите порог фильтрации шума в разностной кртинке'))
st.write('Порог фильтрации', FILTER_THRESHOLD)

#функция поиска разницы в картинках
def pictures_comparison(im_1, im_2):
	
	im_to_compare = np.array(im_2)
	
	#ищем разницу между массивами и фильтруем одну из картинок по разностному массиву
	delta = abs(np.array(im_2) - np.array(im_1))
	im_to_compare[im_to_compare[:, :, :] <120] = im_to_compare[im_to_compare[:, :, :] <120]*2
	im_to_compare[:,:,0][delta[:,:,0]>FILTER_THRESHOLD] = 255
	im_to_compare[:,:,1][delta[:,:,1]>FILTER_THRESHOLD] = 0
	im_to_compare[:,:,2][delta[:,:,2]>FILTER_THRESHOLD] = 0
	
	result_delta = Image.fromarray(im_to_compare, 'RGB')
	result_delta.save('output/result.jpg')
	return result_delta

#делаем кнопку запуска блока расчета прогноза и под нее заводим сам расчет прогноза
result = st.button('Получите сравнительную картинку')

if result:	
	st.image(pictures_comparison(im_1, im_2), caption='На этой картинке красным цветом выделена разница между сравниваемыми картинками')
	
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

#else:
#	st.write('## **Что-то пошло не так, позвоните сисадмину!**')
