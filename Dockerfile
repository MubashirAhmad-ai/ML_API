# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# COPY ./requirements.txt /app/requirements.txt

# RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# COPY ./app /app/app

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application files
COPY ./app /app/app