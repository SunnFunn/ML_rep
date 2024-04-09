# **Проекты с применением DL**
___________________________________________________________________________

```
В репозитории представлено несколько проектов, выполненных в основном с применением методов Deep Learning.
Перечень проектов и их краткое описание представлены ниже.
Подробное описание структуры проектов и подходов, используемых в их исполнении, представлено отельно в описательных файлах
внутри папок проектов.
```
# Содержание <a name="content"></a>

- [1. Приложение оценки риска заболевания сердца по текущему состоянию пациента](#heart)
- [2. Приложение генерации нескольких вариантов русских фамилий с выбранным желаемым началом фамилии](#surnames)
- [3. Приложение анализа эмоциональной окраски текста](#sentiments)
- [4. Приложение сравнительного анализа текстов и чертежей pdf файлов с целью идентификации и маркировки разностей документов](#pictures)
- [5. Приложение выбора оптимальной температуры подачи теплоносителя для отопления промышленных помещений](#heat)
- [6. Приложение выбора оптимальной температуры подачи теплоносителя для отопления промышленных помещений с использование RL модели](#heatRL)



### **1. Оценка риска заболевания сердца** <a name="heart"></a>

Резюме проекта:
> - [Проект](https://github.com/SunnFunn/ML_rep/tree/master/heart) выполнен как web-приложение с интерфейсом, позволяющим вводить текущие данные о состоянии пациента и получать прогнозное значение вероятности заболевания сердца пациента;
> - Прогноз вероятности заболевания осуществляется моделью ExtraTreesClassifier, обученной на [датасете](https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset), взятом из базы датасетов сайта kaggle.com;
> - Интерфейс работы с моделью выполнен с применением модуля streamlit;
> - Приложение контейнеризовано в Docker и развернуто в облачной виртуальной машине с возможностью публичного доступа через web-сервер nginx;

:arrow_up: [Содержание](#content)

### **2. Генерация фамилий** <a name="surnames"></a>

Резюме проекта:
> - [Проект](https://github.com/SunnFunn/ML_rep/tree/master/surnames) выполнен как web-приложение с интерфейсом, позволяющим регистрировать данные нового пользователя, вводить пользователем первые буквы/букву (в разном количестве) фамилии, получать сгенерированные моделью образцы русских фамилий, а также сохранять в базе данных приложения историю запросов к модели;
> - Генерация фамилий осуществляется моделью с использованием реккурентных GRU слоев;
> - Тренировка модели осуществлялась на датасете русских фамилий в латинском написании;
> - Приложение написано с использованием фреймворка Flask;
> - Приложение контейнеризовано в Docker и развернуто в облачной виртуальной машине с возможностью публичного доступа через web-сервер nginx, работающим с Flask приложением через middleware uWSGI;

:arrow_up: [Содержание](#content)

### **3. Анализ эмоциональной окраски текста** <a name="sentiments"></a>

Резюме проекта:
> - [Проект](https://github.com/SunnFunn/ML_rep/tree/master/sentiment_classification) выполнен как web-приложение с интерфейсом, позволяющим регистрировать данные нового пользователя, вводить пользователем текст, имеющий эмоциональную окраску, получать оценку эмоциональной окраски текста моделью, а также сохранять в базе данных приложения историю запросов к модели и результатов ее оценок;
> - Оценка эмоциональной окраски текста осуществляется моделью Transformer;
> - Приложение написано с использованием фреймворка Flask;
> - Оценка моделью текста осуществляется в отдельном сервисе (модуль model_service) с возможностью создания нескольких, параллельно работающих сервисов (workers);
> - Взаимодействие сервиса модели и сервиса flask осушествляется через асинхронного брокера сообщений RabbitMQ;
> - Приложение контейнеризовано в Docker и развернуто в облачной виртуальной машине с возможностью публичного доступа через web-сервер nginx, работающим с Flask приложением через middleware uWSGI, обмен данными между flask контейнером и контейнером модели осуществляется в docker network через контейнер rabbitmq;

:arrow_up: [Содержание](#content)

### **6. Диспетчерское управление температурой теплоносителя с помощью RL model** <a name="heatRL"></a>

Резюме проекта:
> - [Проект](https://github.com/SunnFunn/ML_rep/tree/master/heat_RL) выполнен как modbus server с имитацией modbus client для целей тестирования modbus server;
> - Сервер работает в асинхронном режиме с использованием моделя asyncio python коммуницируя с holding registers (чтение и запись данных в регистры) по локальному ip адресу на порте 5020;
> - работа сервера заключается в чтении регистра с температурой воздуха в помещении (передается в регистры от modbus client), запуске RL (reinforcement learning) модели для оценки температуры теплоносителя, необходимой для поддержки заданной температуры воздуха внутри помещения, записи данных, полученных от RL модели в регистры для считаывания данных modbus client;
> - сервер также записывает опыт, полученный моделью в [файл опыта](https://github.com/SunnFunn/ML_rep/tree/master/heat_RL/data) для актуализации модели;
> - RL модель обучена на основе DDPG (deep determenistic policy gradient);
> - RL модель обновляется шаге опыта (часть первых слоев при этом заморожена);
> - для целей формирования state для RL модели, используемого в функции политики, опрашивается [сайт погоды](https://rp5.ru/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5_(%D0%92%D0%94%D0%9D%D0%A5)), с котрого берутся данные о текущих температуре наружного воздуха, скорости ветра, влажности, облачности.
> - сервер запускается на определенный период (задается параметрами), модель работает циклически с периодом 1 раз в 3 часа;

:arrow_up: [Содержание](#content)
