# Paddle OCR as a Http Service

Exposing Paddle OCR as http service using flask.

How to use:

```shell
docker build -t paddle-ocr-service .
```

Run docker in container

```shell
docker run -d paddle-ocr-service -p 5000:5000 --name my-container-name 
```
