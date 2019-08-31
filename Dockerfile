FROM python:3.7-slim

RUN mkdir -p /code/src
WORKDIR /code
ADD requirements.txt /code/
ADD ./src /code/src
RUN pip --no-cache-dir install -r requirements.txt

ENTRYPOINT ["python", "-m", "src.ingest"]
