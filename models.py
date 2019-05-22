from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import TEXT, INTEGER

Base = declarative_base()


class Indexword(Base):
    __tablename__ = 'indexword'

    word = Column(TEXT, primary_key=True, nullable=False)


class Posting(Base):
    __tablename__ = 'posting'

    word = Column(TEXT, ForeignKey('indexword.word'), primary_key=True, nullable=False)
    documentName = Column(TEXT, primary_key=True, nullable=False)
    frequency = Column(INTEGER, nullable=False)
    indexes = Column(TEXT, nullable=False)



