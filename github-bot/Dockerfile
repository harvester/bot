FROM python:3.8.15-alpine3.15

COPY requirements.txt /srv
WORKDIR /srv
RUN pip install -r requirements.txt

COPY . /srv

CMD ["gunicorn", "harvester_github_bot:app"]
