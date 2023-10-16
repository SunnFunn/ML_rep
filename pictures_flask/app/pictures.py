import numpy as np

import PIL
from PIL import Image, ImageChops, ImageOps
from pdf2image import convert_from_path, convert_from_bytes

def img_converter(file_1, file_2):
	im_1 = []
	im_1.append(Image.open(file_1))
	im_2 = []
	im_2.append(Image.open(file_2))
	
	return im_1, im_2

#функция поиска разницы в картинках
def get_pictures_difference(im_1, im_2, FILTER_THRESHOLD):
	
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


def main(FILTER_THRESHOLD, file_1, file_2):
	im_1, im_2 = img_converter(file_1, file_2)
	diff_inv_red = get_pictures_difference(im_1, im_2, FILTER_THRESHOLD)
	result = get_pictures_blend(diff_inv_red, im_2)
	
	return result
