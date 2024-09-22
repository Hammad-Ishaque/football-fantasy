# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables for Python buffering and Django settings
ENV PYTHONUNBUFFERED 1

# Create and set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt /app/
RUN pip install --no-cache-dir -r base.txt

# Copy the current directory contents into the container at /app
COPY . /app/
