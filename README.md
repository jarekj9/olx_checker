# OLX-link price scrapper

Web-app page takes link to olx and optionally some words to ignore in items titles.
Then it provides average price, median and item count.
It ignores promoted items and shows progress bar.

![Screenshot](screenshot.png?raw=true "Screenshot")

## How

Front-end is made with React and back-end is Flask.
It is ready to be contenerized (docker/gunicorn/nginx) with commands:

```
cd app
yarn install
yarn build
cd ..
docker-compose up -d
```

or for test on dev server:

```
cd app/api
flask run
```
+
```
cd app
yarn start
```
