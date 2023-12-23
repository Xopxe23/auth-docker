FROM python:latest

RUN mkdir /users

WORKDIR /users

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x /users/app.sh
