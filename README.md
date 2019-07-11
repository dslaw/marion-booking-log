# Marion Booking Log

Scrape the Marion County, Oregon booking log.


## Usage

First create a Postgres (11+) database. `docker` can be used to create a
database for development:

```bash
docker run \
    -d \
    -p ${POSTGRES_PORT}:5432 \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_DB=${POSTGRES_DATABASE} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    --name=marion-jail-dev \
    postgres:11
```

Then create a virtual environment using `conda` that the scraper will run in:

```bash
conda create \
    --name=marion-jail \
    --channel=conda-forge \
    --yes \
    python=3.7 \
    --file=requirements.txt
```

Before running anything, first ensure the following environment variables are
set and exported:

* `POSTGRES_HOST`
* `POSTGRES_PORT`
* `POSTGRES_DATABASE`
* `POSTGRES_USER`
* `POSTGRES_PASSWORD`

From within the activated environment, create the database tables:

```bash
python -m src.models
```

and run the scraper:

```bash
python -m src.scrape >> scrape.log
```
