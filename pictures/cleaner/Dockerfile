FROM python:3.9-alpine

RUN adduser ------;echo '------------------' | chpasswd
USER --------

WORKDIR /app
COPY --chown=------:---------- . .
RUN mkdir /app/app
RUN mkdir /app/app/static
RUN mkdir /app/app/static/outputs
RUN chown -R -------:---------- .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "cleaner.py"]
