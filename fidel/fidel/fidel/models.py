from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    JSON,
    Float,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

import datetime

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def _get_date():
    return datetime.datetime.now()

class Zone(Base):
    __tablename__ = 'zone'
    id = Column(Integer, primary_key=True)
    acronym = Column(Text, nullable=False)
    polygon = Column(JSON, nullable=False)
    dateadd = Column(DateTime, nullable=False, default=_get_date)

class Property(Base):
    __tablename__ = 'property'
    id = Column(Integer, primary_key=True)
    acronym = Column(Text, nullable=False)
    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
