FROM python:3.8

WORKDIR /code

COPY . /code/

RUN pip install -r /code/requirements.txt

CMD python -m src.clock

FROM ubuntu:20.10

# Install Chrome for Selenium
RUN apt-get update && apt-get install -y \
curl
RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb
RUN dpkg -i /chrome.deb || apt-get install -yf
RUN rm /chrome.deb

# Install chromedriver for Selenium
RUN curl https://chromedriver.storage.googleapis.com/2.31/chromedriver_linux64.zip -o /usr/local/bin/chromedriver
RUN chmod +x /usr/local/bin/chromedriver