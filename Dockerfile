# Use an official Python runtime as the parent image
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --default-timeout=1000 --no-cache-dir -v -v -v -r requirements.txt
COPY . /app

# Run main.py when the container launches
CMD ["python3", "main.py"]
