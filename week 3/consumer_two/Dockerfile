# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Update package lists and install required packages
RUN apt-get update && \
    apt-get install -y pkg-config libmariadb-dev-compat build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create a directory for the application
RUN mkdir /app

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script into the container
COPY item_creation.py /app/

# Run item_creation.py when the container launches
CMD ["python", "item_creation.py"]
