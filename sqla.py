# lolreg.sqla package

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension
from zope.interface import implements

from lolreg.interfaces import IRegistrationBackend

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

from sqlalchemy import engine_from_config

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    # etc

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    # etc

class SQLARegistrationBackend(object):
    implements(IRegistrationBackend)
    def __init__(self, settings):
        engine = engine_from_config(settings, 'lol.sqlalchemy.')
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        Base.metadata.create_all(engine)

    def add_user(self, **kw):
        session = DBSession()
        user = User(**kw)
        session.add(user)

    def add_group(self, whatever):
        # whatever
        pass

    def activate(self, token):
        # whatever
        pass
