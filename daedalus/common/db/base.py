'''Classes for working with DB through SQLAlchemy.'''

import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base

from daedalus.config import POSTGRES_URL

Base = declarative_base() #pylint: disable=C0103
Base.metadata.naming_convention = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s"
}

def connect(dsn=POSTGRES_URL):
    ''' initialize the engine '''
    return sqlalchemy.create_engine(dsn)
