from bs4 import BeautifulSoup
import requests as req
import urllib3

import re
from app import current_hour

urllib3.disable_warnings()

def get_temperatures_forecast(url):
	response = req.get(url, headers = {'user-agent': 'Edg/95.0.1020.53'}, timeout=50, verify=False)
	page = BeautifulSoup(response.text, 'html.parser')

	#содержимое таблицы на странице прогноза погоды на 7 суток
	table_content = page.find('table', {'id': 'forecastTable_1_3'})

	# парсинг текущей температуры наружного воздуха и прогноза температуры через 3 часа
	temperatures_list = table_content.find_all('div', {'class': 't_0'})
	temperature_current = float(temperatures_list[0].text)
	temperature_next = float(temperatures_list[3].text)

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

	return temperature_current, temperature_next, wind, humidity, cloudiness