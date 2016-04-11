FROM python:2-onbuild

RUN apt-get update && apt-get install -y postgresql-client libpq-dev

ADD . daedalus/
WORKDIR daedalus/
RUN pip install -r requirements.txt
EXPOSE 5000
