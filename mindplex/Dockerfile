FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /snetrecommender
WORKDIR /snetrecommender


RUN apt update
RUN apt -y install gcc
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt --timeout 600
RUN [ "python", "-c", "import nltk; nltk.download('stopwords')" ]
COPY . /snetrecommender