import streamlit as st
import PIL
from PIL import ImageFilter

def settings():
	
	#выводим настроечную панель
	st.markdown("<h3 style='text-align: center; color: darkgrey;'>Настройка параметров анализа картинок:</h3>", unsafe_allow_html=True)
	
	#выводим линейку чувствительности модели к разности картинок
	distance_thresh = st.slider('Порог чувствительности модели', 0.4, 1.0, 0.89)
	st.write("Порог чувствительности:", distance_thresh)
	
	#выводим линейку изменения разрешения фалов png после конвертации в них из pdf
	dpi = st.slider('Качество конвертации pdf в jpeg', 100, 300, 250)
	st.write("dpi:", dpi)
	
	#выводим панель задания размера ядра размытия областей с разными пикселями
	rect_width = st.number_input('Ширина ядра размытия', 5, 100, 20, 1)
	rect_height = st.number_input('Высота ядра размытия', 1, 20, 5, 1)
	st.write('Ядро размытия:', (rect_width, rect_height))
	kernel = (rect_width, rect_height)
	
	#выводим панель количество итераций размытия областей с разными пикселями
	iterations = st.number_input('Итерации размытия', 1, 10, 2, 1)
	st.write('Количество итераций:', iterations)
	
	#выводим панель выбора фильтра разностной картинки для более стабильного поиска контуров разностных областей
	im_filter_dict = {'EDGE_ENHANCE': ImageFilter.EDGE_ENHANCE, 'EDGE_ENHANCE_MORE': ImageFilter.EDGE_ENHANCE_MORE,
				'SMOOTH': ImageFilter.SMOOTH, 'SMOOTH_MORE': ImageFilter.SMOOTH_MORE, 'SHARPEN': ImageFilter.SHARPEN,
				'DETAIL': ImageFilter.DETAIL, 'FIND_EDGES': ImageFilter.FIND_EDGES, 'BLUR': ImageFilter.BLUR}
	
	filter_name = st.selectbox('Выбор фильтра картинок', ('EDGE_ENHANCE_MORE', 'EDGE_ENHANCE', 'SMOOTH', 'SMOOTH_MORE',
										'SHARPEN', 'DETAIL', 'FIND_EDGES', 'BLUR'))
	st.write('Выбран фильтр:', filter_name)
	im_filter = im_filter_dict[filter_name]
	
	#выводим линейку затененности фоновой картинки в сравнеии с выделенными боксами
	blend_level = st.slider('Уровень затененности фоновой картинки', 0.1, 1.0, 0.2, 0.1)
	st.write("Затененность:", blend_level)
	
	return distance_thresh, dpi, kernel, iterations, im_filter, blend_level
