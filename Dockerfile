FROM python:latest

WORKDIR /redfriend
COPY . /redfriend
RUN pip install -r requirements.txt