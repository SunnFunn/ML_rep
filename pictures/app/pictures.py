import numpy as np
import streamlit as st

from PIL import Image, ImageChops
import PIL.ImageOps

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

#@st.cache
def load_image(image_file):
	img = Image.open(image_file)
	return img

img_file_buffer_1 = st.file_uploader("Загрузите первую картинку")
img_file_buffer_2 = st.file_uploader("Загрузите вторую картинку")

if img_file_buffer_1 and img_file_buffer_2 is not None:
	
    im_1 = load_image(img_file_buffer_1)
    im_2 = load_image(img_file_buffer_2)
else:
	st.write('## **Вы не загрузили одну или обе картинки!**')

#функция поиска разницы в картинках
def pictures_diff(im_1, im_2):
	#ищем разницу между картинками
	result_delta=ImageChops.difference(im_1, im_2)
	
	#инвертируем картинку
	inverted_image = PIL.ImageOps.invert(result_delta)
	
	#преобразуем картинку в числовой массив, фильтруем его, чтобы выделить разницу в красный цвет
	#и преобразуме обратно в картинку
	inv_image_array = np.array(inverted_image)
	inv_image_array[:,:,0][inv_image_array[:,:,0]<200] = 255
	inv_image_array[:,:,1][inv_image_array[:,:,1]<200] = 0
	inv_image_array[:,:,2][inv_image_array[:,:,2]<200] = 0
	diff_image = Image.fromarray(inv_image_array, 'RGB')
	
	return diff_image

#функция наложения разницы и второй картинки
def overlayed_images(diff_image, im_2):
	
	#накладываем разницу на вторую картинку с затенением второй картинки
	overlayed_images = Image.blend(im_2, diff_image, 0.8)
	
	return overlayed_images

#функция сохранения наложенной картинки
def saving_result_image(overlayed_images):
	overlayed_images.save('output/result.jpg')

#делаем кнопку запуска блока расчета прогноза и под нее заводим сам расчет прогноза
result = st.button('Получите сравнительную картинку')

if result:
	
	diff_image = pictures_diff(im_1, im_2)
	overlayed_images = overlayed_images(diff_image, im_2)
	
	st.image(diff_image, caption='Вот как выглядит разница между вашими картинками')
	st.image(overlayed_images, caption='Вот как выглядит разница на фоне второй картинки')
	
	
#делаем кнопку сохранения картинки
save_result = st.button('Сохраните сравнительную картинку')
if save_result:
	
	diff_image = pictures_diff(im_1, im_2)
	overlayed_images = overlayed_images(diff_image, im_2)
	saving_result_image(overlayed_images)
	st.success('файл сохранен')
	
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
