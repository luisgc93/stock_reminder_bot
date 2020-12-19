FROM python:3.8

WORKDIR /code

COPY . /code/

RUN pip install -r /code/requirements.txt

CMD ["python -m src.models", "python -m src.clock"]