FROM python:3.9-slim-buster

WORKDIR /code

RUN pip install -r /code/requirements.txt

COPY . /code/

CMD python -m src.clock
