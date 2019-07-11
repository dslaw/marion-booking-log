from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import logging
import sys

from src.common import make_database_uri
from src.models import Batch, Charge, Inmate
from src.scrape import scrape


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def create_session():
    uri = make_database_uri()
    engine = create_engine(uri)
    Session = sessionmaker(bind=engine)
    return Session()


def main():
    logging.info("Starting database session")
    session = create_session()

    try:
        logging.info("Starting scraping")
        ents = scrape()
    except Exception:
        logging.exception("Scraping failed")
        return 1

    logging.info("Scraped %s inmates", len(ents))

    try:
        previous_batch, *_ = session.query(
            func.coalesce(func.max(Batch.id), 0)
        ).one()
        current_batch = previous_batch + 1

        batch = Batch(id=current_batch)
        session.add(batch)
        session.flush()

        for ent in ents:
            inmate = Inmate(
                batch_id=batch.id,
                booking_id=ent["booking_id"],
                name=ent["name"],
                race=ent["race"],
                sex=ent["sex"],
                height=ent["height"],
                weight=ent["weight"],
                hair=ent["hair"],
                eyes=ent["eyes"],
                booking_date=ent["date_booked"],
                next_court_date=ent["court_date"],
                bail=ent["bail"],
            )
            inmate.charges = [
                Charge(**charge, batch_id=batch.id)
                for charge in ent["charges"]
            ]

            session.add(inmate)
    except Exception:
        logging.exception("Persisting data failed")
        return 1

    session.commit()
    logging.info("Persisted scraped data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
