from bs4 import BeautifulSoup
import requests as req
import lxml.html as html
import urllib3

header = {'user-agent': 'Edg/95.0.1020.53'}
urllib3.disable_warnings()
url = 'https://rp5.ru/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%95%D0%BA%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%BD%D0%B1%D1%83%D1%80%D0%B3%D0%B5'

response = req.get(url, headers=header, timeout=50, verify=False)
page = BeautifulSoup(response.text,'html.parser')

def get_temperatures_forecast(tags_1,tags_2, tags_3, ids, classes_1, classes_2, forecast_hours):
	temperatures = page.find(tags_1, {'id': ids}).find_all(tags_2, {'class': classes_1})
	all_temperatures = []
	for temp in temperatures:
		all_temperatures.append(temp.find(tags_3, class_=classes_2).text)
	outside_temperature = []
	for i in range(forecast_hours):
		outside_temperature.append(int(all_temperatures[i]))
	
	return outside_temperature
