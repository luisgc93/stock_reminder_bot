FROM python:3.9-slim-buster

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

COPY . /code/

CMD python -m src.clock
