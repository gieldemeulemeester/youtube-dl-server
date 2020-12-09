[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://raw.githubusercontent.com/manbearwiz/youtube-dl-server/master/LICENSE)

# youtube-dl-server

[`Flask`](https://github.com/pallets/flask) application for [`youtube-dl`](https://github.com/rg3/youtube-dl) for downloading youtube videos to a server. The docker image is based on [`python:alpine`](https://registry.hub.docker.com/_/python/).

![screenshot][1]

## Running

### Docker

This example uses the `docker build` command to build the image and the `docker run` command to create a container from that image. The container exposes port 5000 and volume `/youtube-dl`.

```shell
docker build --tag youtube-dl-server .
docker run -d --name youtube-dl -p 5000:5000 -v ~/volumes/youtube-dl:/youtube-dl youtube-dl-server
```

### Docker Compose

This is an example service definition that could be added in `docker-compose.yml`.

```yml
youtube-dl:
  container_name: youtube-dl
  build: ./services/youtube-dl/
  volumes:
    - ./volumes/youtube-dl:/youtube-dl
  ports:
    - 5000:5000
  restart: unless-stopped
```
Optionally you could make the download directory accessible with samba as shown in the example below.

```yml
samba:
  image: dperson/samba:latest
  environment:
    - USER=<insert user>;<insert password>
    - SHARE=youtube-dl;/mnt/youtube-dl;yes;no;yes;<insert user>;<insert user>
  volumes:
    - ./volumes/youtube-dl:/mnt/youtube-dl
  ports:
    - 137:137/udp
    - 138:138/udp
    - 139:139/tcp
    - 445:445/tcp
  restart: unless-stopped
```

Then run `docker-compose up -d --build`.

### Python

If you have python 3 installed in your PATH you can simply run like this, providing optional environment variable overrides inline.

```shell
sudo YDL_SERVER_PORT=8123 python3 -u ./flask-server.py
```

## Usage

### Web

Just navigate to `http://{{host}}:5000/` and paste the video url or select .webloc files to the video's and click the *Submit* button.
Navigate to the *Jobs* tab to track download progress.

### Curl

```shell
curl -X POST --data-urlencode "url={{url}}" http://{{host}}:5000/enqueue-url
```

### Fetch

```javascript
fetch(`http://${host}:5000/enqueue-url`, {
  method: "POST",
  body: new URLSearchParams({
    url: url,
    format: "bestvideo"
  }),
});
```

### Bookmarklet

Add the following bookmarklet to your bookmark bar so you can conviently send the current page url to your youtube-dl-server instance.

```javascript
javascript:!function(){fetch("http://${host}:5000/enqueue-url",{body:new URLSearchParams({url:window.location.href,format:"bestvideo"}),method:"POST"})}();
```


[1]:youtube-dl-server.png
