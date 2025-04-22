# Use an official base image
FROM python:3.10-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install necessary packages
# use apt to install tesseract-ocr in this container
# see instructions here: https://tesseract-ocr.github.io/tessdoc/Installation.html
# RUN apt-get update # <your code here> #Checkout documentation on RUN here: https://docs.docker.com/engine/reference/builder/#run

RUN apt-get update && apt-get -y install poppler-utils ffmpeg libsm6 libxext6 && \
    pip3 --no-cache-dir install --upgrade pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Tesseract OCR and any dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    # Add any other dependencies needed by your app here
    && rm -rf /var/lib/apt/lists/* # Clean up apt cache

# Copy the application code
COPY /src /app
COPY requirements.txt /app

# Set the working directory
WORKDIR /app

# Install with pip any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the script
# Default command - typically overridden by docker-compose run
CMD ["python", "app.py"]

