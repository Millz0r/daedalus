''' Session wrapper '''
import functools

from sqlalchemy.orm import sessionmaker

from daedalus.common.db.base import connect

class DBSession(object): #pylint: disable=R0903
    ''' Decorator to create a session. '''

    SESSIONMAKER = None

    def __init__(self, engine=connect(), auto_commit=True):
        '''
        Initialize the decorator with the `engine` and set `auto_commit` flag.
        '''
        assert engine is not None, "Must pass a valid engine parameter"
        self._auto_commit = auto_commit
        if DBSession.SESSIONMAKER is None:
            DBSession.SESSIONMAKER = sessionmaker(expire_on_commit=True, bind=engine)

    def __call__(self, func):
        ''' the actual decorator '''
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            '''
            Initialize the session and handle commit and rollback
            '''
            db_session = DBSession.SESSIONMAKER()
            try:
                kwargs["_db_session"] = db_session
                # the session gets injected in the method kwargs as `_db_session`
                results = func(*args, **kwargs)
                db_session.commit()
                # should we rollback for safety?
                if not self._auto_commit:
                    db_session.rollback()
            except:
                db_session.rollback()
                raise
            finally:
                # release the session back to the connection pool
                db_session.close()
            return results
        return wrapper
