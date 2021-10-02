FROM python:3.9-slim-buster

WORKDIR /code

COPY . /code/

RUN pip install -r /code/requirements.txt

CMD python -m src.clock
