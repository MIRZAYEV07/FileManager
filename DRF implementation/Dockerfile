# Use an official Python runtime as the base image
FROM python:3.9-slim

WORKDIR /app
RUN apt-get update --fix-missing && \
    apt-get install -y ffmpeg libsm6 libxext6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD ../FastAPI%20implementation/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt


ADD ../FastAPI%20implementation /app




