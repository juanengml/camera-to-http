FROM python:3.8

RUN apt-get update

RUN mkdir /app

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
