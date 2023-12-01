FROM python:3.10

RUN apt-get update && apt-get install -y r-base

COPY . /src

WORKDIR /src

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "app/main.py" ]
