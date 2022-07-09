from mindplex.celery import app
from celery import shared_task
import requests

@shared_task
def relearnerTask():
    URL =r"http://localhost:8000/relearner/user-based/item-based/"
    return requests.get(url=URL)




