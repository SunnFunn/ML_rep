from bs4 import BeautifulSoup
import requests as req
import urllib3

import re
from app import current_hour

header = {'user-agent': 'Edg/95.0.1020.53'}
urllib3.disable_warnings()
url = 'https://rp5.ru/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%95%D0%BA%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%BD%D0%B1%D1%83%D1%80%D0%B3%D0%B5'

response = req.get(url, headers=header, timeout=50, verify=False)
page = BeautifulSoup(response.text,'html.parser')

def get_temperatures_forecast():
	#содержимое таблицы на странице прогноза погоды на 7 суток
	table_content = page.find('table', {'id': 'forecastTable_1_3'})

	# парсинг текущей температуры наружного воздуха
	temperature = float(table_content.find('div', {'class': 't_0'}).text)

	#парсинг текущей скорости ветра
	winds = table_content.find_all('div', {'class': 'wv_0'})
	wind = float(winds[0].text)

	# парсинг текущей влажности воздуха
	if current_hour >= 8 and current_hour <= 18:
		humidities = table_content.find('tr', {'class': 'brief'}).find_all('td', {'class': ['d underlineRow',
																				  			'd underlineRow blue',
																							'd underlineRow red']})
	else:
		humidities = table_content.find('tr', {'class': 'brief'}).find_all('td', {'class': ['n underlineRow',
																							'n underlineRow blue',
																							'n underlineRow red']})
	humidity = float(humidities[0].text)/100

	# парсинг текущей облачности
	cloudiness_info = table_content.find('div', {'class': 'cc_0'}).find('div')['onmouseover']
	cloudiness = float(re.sub('[^0-9]', '', cloudiness_info)[:2])/100

	return temperature, wind, humidity, cloudiness