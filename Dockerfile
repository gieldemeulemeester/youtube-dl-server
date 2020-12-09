FROM python:alpine

RUN apk add --no-cache \
  ffmpeg \
  tzdata

WORKDIR /usr/src/app
VOLUME /youtube-dl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .
RUN chmod u+x ./*.py

EXPOSE 5000

HEALTHCHECK CMD curl --fail http://localhost:5000 || exit 1
ENTRYPOINT [ "python", "flask-server.py" ]
