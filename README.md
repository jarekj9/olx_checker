# OLX-link price scrapper

Web-app page takes link to olx and optionally some words to ignore in items titles.
Then it provides average price, median and item count.
It ignores promoted items and shows progress bar.

## How

Front-end is made with React and back-end is Flask.
It is ready to be contenerized with:

```
cd app
yarn install
yarn build
cd ..
docker-compose up -d
```
