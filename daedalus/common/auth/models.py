''' Classes to handle request authentication '''

from sqlalchemy import Column, String

from daedalus.common.db import Base, SurrogatePK

class Caller(SurrogatePK, Base): #pylint: disable=R0903
    ''' Holds details about an authorized caller '''

    __tablename__ = 'callers'

    username = Column(String(32), index=True)
    token = Column(String(128), index=True)
    # TODO switch to an encrypted token # pylint: disable=fixme
    #secret_token = Column(BcryptType)
    description = Column(String())
