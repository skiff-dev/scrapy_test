from sqlalchemy import Column, String, ForeignKey, Integer, Date
from sqlalchemy.orm import relation, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.sqltypes import Date
from sqlalchemy import create_engine, select, update
import os.path


Base = declarative_base()


class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    birthday = Column(Date)
    bio = Column(String(150))
    quote = relationship("Quote")


assotiation_table = Table(
    "assotiation",
    Base.metadata,
    Column("keyword_id", ForeignKey("keyword.id")),
    Column("quote_id", ForeignKey("quote.id")),
)


class Keyword(Base):
    __tablename__ = "keyword"
    id = Column(Integer, primary_key=True)
    word = Column(String(40), nullable=False, unique=True)
    quotes = relationship(
        "Quote", secondary=assotiation_table, back_populates="keywords"
    )


class Quote(Base):
    __tablename__ = "quote"
    id = Column(Integer, primary_key=True)
    quote = Column(String, nullable=False, unique=True)
    author_id = Column(Integer, ForeignKey("author.id"))
    keywords = relationship(
        "Keyword", secondary=assotiation_table, back_populates="quotes"
    )


def init_db():
    if not os.path.exists("test.db"):
        engine = create_engine("sqlite:///test.db")
        Base.metadata.create_all(engine)


def test_many_to_many():
    engine = create_engine("sqlite:///test.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    q = session.execute(select(Quote).where(Quote.id == 1)).scalar_one()
    q1 = session.execute(select(Quote).where(Quote.id == 2)).scalar_one()
    q2 = session.execute(select(Quote).where(Quote.id == 3)).scalar_one()
    kw = session.execute(select(Keyword).where(Keyword.id == 1)).scalar_one()
    kw.quotes = [q, q1, q2]

    session.add(kw)
    session.commit()
    session.close()


def test_quote():
    engine = create_engine("sqlite:///test.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    for quotes in session.query(Keyword).filter(Keyword.word == "truth").all():
        print([quote.quote for quote in quotes.quotes])


if __name__ == "__main__":
    init_db()
    # test_quote()
