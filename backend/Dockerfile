FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code/backend
# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /code/backend
# Connect web service to db service
RUN apt-get update && apt-get install -y libpq-dev \
    gcc \ 
    postgresql-client
RUN pip install psycopg2==2.8.4
RUN apt-get autoremove -y gcc