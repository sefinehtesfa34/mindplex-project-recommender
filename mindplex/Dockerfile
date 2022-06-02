FROM python:3.9.5-alpine
LABEL maintainer = "mindplex.com"
WORKDIR  /recommender

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt  /recommender/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /recommender/

RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
USER appUser