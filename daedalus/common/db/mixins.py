''' Mixins used to add behaviours to SQLAlchemy classes '''

from sqlalchemy import Column, Integer

class SurrogatePK(object): #pylint: disable=R0903
    """A mixin that adds a surrogate integer 'primary key' column named
    `id` to any declarative-mapped class."""

    id = Column(Integer, primary_key=True) #pylint: disable=R0903, C0103
