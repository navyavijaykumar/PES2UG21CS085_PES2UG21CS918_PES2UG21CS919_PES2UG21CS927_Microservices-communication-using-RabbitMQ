# Use an official Python runtime as a parent image
FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y pkg-config libmariadb-dev-compat build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY stock_management.py /app/

CMD ["python", "stock_management.py"]
