### **Анализ эмоциональной окраски текста**

[Проект](https://github.com/SunnFunn/ML_rep/tree/master/sentiment_classification) выполнен как web-приложение с интерфейсом, позволяющим регистрировать данные нового пользователя, вводить пользователем текст, имеющий эмоциональную окраску, получать оценку эмоциональной окраски текста моделью, а также сохранять в базе данных приложения историю запросов к модели и результатов ее оценок;

Интерфейсы регистрации пользователя, ввода текста и получения оценки эмоциональной окраски представлены ниже на трех скриншотах.

![sentiments_1](https://github.com/SunnFunn/ML_rep/blob/master/imgs/sentiments_1.png)


![sentiments_2](https://github.com/SunnFunn/ML_rep/blob/master/imgs/sentiments_2.png)


![sentiments_3](https://github.com/SunnFunn/ML_rep/blob/master/imgs/sentiments_3.png)

Приложение развернуто на VM AWS в четырех докер контейнерах (в случае одного worker, для каждого дополнительного worker создается новый контейнер): web-контейнер, контейнер flask-приложения с uWSGI сервером, контейнер брокера сообщений rabbitmq и worker-контейнер (выполняет основную работу инференса трансформера-классификатора по поступившему запросу) с запуском контейнеров через конфигурацию в docker-compose.yml.
Контейнер flask-приложения создается с новым пользователем внутри контейнера и с передачей прав собственника всех файлов (рекурсивно) данному пользователю (в целях ухода от root собственника).
Конфигурация uWSGI представлена в фалйе sentiments.ini и включает механизм гибкого изменения количества процессов сервера от 2 до 10 в зависимости от нагрузки. Статистика uWSGI сервера доступна на порте 9000.
Конфигурация nginx proxy server в целом стандартная.

Контейнеры взаимодействую в следующей схеме:

> - flask-приложение обрабатывает ввод-вывод запросов через web-интерфейс и отправляет полученные запросы по схеме RPC через очередь брокера сообщений одному из workers
> - rabbitmq создает очереди ведет асинхронную обработку запросов/ответов
> - дополнительно flask-приложение сохраняет обращения и результаты их обработки отдельно по каждому зарегистрированному пользоватлю в базу данных приложения
> - worker получает запросы от flask-приложения осуществляет инференс (запускаясь как удленная subroutine) и отправляет обратно с correlation-id результат обработки
количество workers задается в конфигурации файла docker-compose.yml в зависимости от нагрузки на приложение

Модель тренировалась отдельно (смотрите файл Emotions_classifie.ipynb). Модель построена как Трансформер-энкодер со следующими основными параметрами:

~~~

Количество классов эмоциональной окраски текста: 6
Размер словаря: 1437 токенов
Количество голов MultiHeadAttention: 6
Слой трансформера: 1
Размерность Embedding пространства токенов: 300

~~~
