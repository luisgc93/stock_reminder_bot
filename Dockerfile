FROM python:3.8

WORKDIR /code

COPY . /code/

RUN pip install -r /code/requirements.txt && python -m src.models

CMD python -m src.models