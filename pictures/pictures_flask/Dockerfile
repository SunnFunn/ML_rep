FROM python:3.9.1

RUN apt-get clean && apt-get update

RUN pip install --upgrade pip
RUN pip3 install opencv-python-headless
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV SECRET_KEY = ------------------------

RUN adduser ----------;echo 'pics:---------------' | chpasswd
USER ---------------

WORKDIR /app
COPY --chown=-----------:--------- . .
RUN chown -R -----:--------------- .

EXPOSE 5000
CMD ["uwsgi", "pics.ini"]
