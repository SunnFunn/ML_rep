### **1. Оценка риска заболевания сердца**

[Проект](https://github.com/SunnFunn/ML_rep/tree/master/heart) выполнен как web-приложение с интерфейсом, позволяющим вводить текущие данные о состоянии пациента и получать прогнозное значение вероятности заболевания сердца пациента. Прогноз вероятности заболевания осуществляется моделью ExtraTreesClassifier, обученной на [датасете](https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset), взятом из базы датасетов сайта kaggle.com.

Интерфейс ввода данных и получения прогноза вероятности заболевания сердца представлен ниже на двух скриншотах. Слева информационная часть интерфейса, разъясняющая характер вводимы данных. Прогноз выдается после ввода данных в процентом значении риска заболеваемости.

![Heart_interface_1](https://github.com/SunnFunn/ML_rep/blob/master/imgs/heart_1.png)


![Heart_interface_2](https://github.com/SunnFunn/ML_rep/blob/master/imgs/heart_2.png)

Приложение развернуто на VM AWS в докер контейнерах: web-контейнер и streamlit-контейнер с запуском контейнеров через конфигурацию в docker-compose.yml.
Конфигурация nginx proxy server в целом стандартная, однако для корректной работы nginx proxy server с приложением streamlit в конфигурационный файл default.conf необходимо добавить в раздел location:


```
-proxy_set_header Upgrade $http_upgrade;
-proxy_set_header Connection "upgrade";

```

Исходные данные, на которых проходила тренировка модели находятся в папке data. Модель тренировалась отдельно (смотрите файл heart.ipynb и сохранена в папке ./streamlit_heart/app/model в формате .pkl.

Точность модели оценивается на следующих уровнях:
~~~

f1 = 0.893, recall = 0.866, precision = 0.922, auc = 0.941
confusion_matrix:
[[100  12]
 [ 22 142]]

~~~
