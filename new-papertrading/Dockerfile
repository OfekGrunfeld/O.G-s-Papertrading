FROM python:3.12.1

WORKDIR /app

COPY . /app

# Copy requirements to keep in cache
COPY ./requirements.txt /app/requirements.txt

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN pip install -r requirements.txt

EXPOSE 5555


CMD ["python", "main.py"]