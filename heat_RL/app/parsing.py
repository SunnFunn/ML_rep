# импорт библиотек для формирования запросов к сайту, получения ответа и поиска нужных данных в ответе от сайта
from bs4 import BeautifulSoup
import requests as req
import urllib3

# библиотека обработки регулярных выражений и библиотека работы с данным формата "дата"
import re
from datetime import datetime

#импорт прогнозного количества часов
from app import forecast_hours

urllib3.disable_warnings()


# функция получения необходимых для работы модели данных с сайта rp.5
def get_temperatures_forecast(url):
    # отправляем запрос к сайту и получаем ответ, далее передаем содержимое страницы в переменную page
    response = req.get(url, headers={'user-agent': 'Edg/95.0.1020.53'}, timeout=50, verify=False)
    page = BeautifulSoup(response.text, 'html.parser')

    # вытаскиваем из page содержимое нужной нам таблицы на странице прогноза погоды на 7 суток
    table_content = page.find('table', {'id': 'forecastTable_1_3'})

    # из этой таблицы вытаскиваем текущую температуру наружного воздуха и прогноз температуры через 3 часа
    temperatures_list = table_content.find_all('div', {'class': 't_0'})
    temperature_current = float(temperatures_list[0].text)
    temperature_next = float(temperatures_list[forecast_hours].text)

    # из этой же таблицы вытаскиваем текущую скорость ветра
    winds = table_content.find_all('div', {'class': 'wv_0'})
    wind = float(winds[0].text)

    # из этой же таблицы вытаскиваем текущую влажность воздуха
    # в разные часы там применяются разные тэги
    if 8 <= datetime.now().hour + 1 <= 18:
        humidities = table_content.find('tr', {'class': 'brief'}).find_all('td', {'class': ['d underlineRow',
                                                                                            'd underlineRow blue',
                                                                                            'd underlineRow red']})
    else:
        humidities = table_content.find('tr', {'class': 'brief'}).find_all('td', {'class': ['n underlineRow',
                                                                                            'n underlineRow blue',
                                                                                            'n underlineRow red']})
    humidity = float(humidities[0].text) / 100

    # из этой же таблицы вытаскиваем текущую облачность
    cloudiness_info = table_content.find('div', {'class': 'cc_0'}).find('div')['onmouseover']
    # из строки оставляем только цифры и берем только первые две цифры
    cloudiness = float(re.sub('[^0-9]', '', cloudiness_info)[:2]) / 100

    return temperature_current, temperature_next, wind, humidity, cloudiness
