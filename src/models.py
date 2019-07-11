from sqlalchemy import Column, Integer, ForeignKey, Sequence, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index, UniqueConstraint
from sqlalchemy.sql.expression import text
from sqlalchemy.types import Date, DateTime


Base = declarative_base()


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, Sequence("batches_id_seq"), primary_key=True)
    created_at = Column(DateTime(timezone=False), server_default=text("now()"))


# XXX: Convert race, sex, hair, eyes to enums once their values are better
#      understood.
class Inmate(Base):
    __tablename__ = "inmates"
    __table_args__ = (
        UniqueConstraint("booking_id", "batch_id"),
    )

    id = Column(Integer, Sequence("inmates_id_seq"), primary_key=True)
    booking_id = Column(String, nullable=False)
    batch_id = Column(ForeignKey("batches.id"), nullable=False)
    name = Column(String, nullable=False)
    race = Column(String, nullable=False)
    sex = Column(String, nullable=False)
    height = Column(Integer, nullable=False)  # Inches.
    weight = Column(Integer, nullable=False)  # Pounds.
    hair = Column(String, nullable=False)
    eyes = Column(String, nullable=False)
    booking_date = Column(Date, nullable=False)
    next_court_date = Column(Date, nullable=True)
    release_date = Column(Date, nullable=True)
    bail = Column(Integer, nullable=True)  # Dollars.


class Charge(Base):
    __tablename__ = "charges"
    __table_args__ = (
        UniqueConstraint("id", "batch_id", "inmate_id"),
        Index("batch_inmate_idx", "batch_id", "inmate_id"),
    )

    id = Column(Integer, Sequence("charges_id_seq"), primary_key=True)
    batch_id = Column(ForeignKey("batches.id"), nullable=False)
    inmate_id = Column(ForeignKey("inmates.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    statute = Column(String, nullable=False)
    release = Column(String, nullable=True)
    authority = Column(String, nullable=False)

    inmate = relationship("Inmate", back_populates="charges")


Inmate.charges = relationship(
    "Charge",
    order_by=Charge.id,
    back_populates="inmate",
    cascade="all, delete, delete-orphan"
)


if __name__ == "__main__":
    # Create tables.
    from sqlalchemy import create_engine
    from .common import make_database_uri

    uri = make_database_uri()
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
