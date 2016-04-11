'''Custom behaviour for SQLAlchemy fields.'''

import bcrypt

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

class Password(str):
    """
    Coerce a string to a bcrypt password.

    Rationale: for an easy string comparison,
    so we can say ``some_password == 'hello123'``

    .. seealso::

        https://pypi.python.org/pypi/bcrypt/

    """

    def __new__(cls, value, salt=None, crypt=True):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if crypt:
            value = bcrypt.hashpw(value, salt or bcrypt.gensalt(4))
        return str.__new__(cls, value)

    def __eq__(self, other):
        if not isinstance(other, Password):
            other = Password(other, self)
        return str.__eq__(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

class BcryptType(TypeDecorator):
    """Coerce strings to bcrypted Password objects for the database."""

    impl = String(128)

    def process_bind_param(self, value, dialect):
        return Password(value)

    def process_result_value(self, value, dialect):
        # already crypted, so don't crypt again
        return Password(value, value, False)

    def process_literal_param(self, value, dialect):
        return Password(value)

    python_type = unicode

    def __repr__(self):
        return "BcryptType()"
