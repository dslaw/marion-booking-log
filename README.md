# Marion Booking Log

Scrape the Marion County, Oregon booking log.


## Usage

First, ensure the following environment variables are set and exported:

* `POSTGRES_PORT`
* `POSTGRES_DATABASE`
* `POSTGRES_USER`
* `POSTGRES_PASSWORD`

Create a Postgres (11+) database. `docker` can be used to create one:

```bash
docker run \
    -d \
    -p ${POSTGRES_PORT}:5432 \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_DB=${POSTGRES_DATABASE} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    --name=marion-jail-db \
    postgres:11
```

Then build the container for the web scraper:

```bash
docker build . --tag=marion-jail-scraper
```

Use the web scraper container to setup the database:

```bash
docker run \
    --rm \
    --net=host \
    -e POSTGRES_HOST=localhost \
    -e POSTGRES_PORT=${POSTGRES_PORT} \
    -e POSTGRES_DATABASE=${POSTGRES_DATABASE} \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    --name=marion-jail-scraper \
    marion-jail-scraper:latest \
    --setup-db
```

And run the scraper, sending logging statements to stdout:

```bash
docker run \
    --rm \
    --net=host \
    -e POSTGRES_HOST=localhost \
    -e POSTGRES_PORT=${POSTGRES_PORT} \
    -e POSTGRES_DATABASE=${POSTGRES_DATABASE} \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    --name=marion-jail-scraper \
    marion-jail-scraper:latest
```
