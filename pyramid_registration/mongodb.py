import pymongo
from pyramid.events import subscriber
from pyramid.events import NewRequest

from zope.interface import implements
from pyramid_registration.interfaces import IRegistrationBackend

class MongoDBRegistrationBackend(object):
    """ MongoDB implementation of RegistrationBackend """
    implements(IRegistrationBackend)

    def __init__(self, settings, config):

        # Make request.db be a reference to MongoDB Database handle
        def add_mongo_db(event):
            settings = event.request.registry.settings
            url = settings['mongodb.url']
            db_name = settings['mongodb.db_name']
            db = settings['mongodb_conn'][db_name]
            event.request.db = db
        db_uri = settings['mongodb.url']
        conn = pymongo.Connection(db_uri)
        def create_indexes(connection):
            """ Create the indexes.
            See http://api.mongodb.org/python/current/api/pymongo/collection.html#pymongo.collection.Collection.create_index"""
            indexes = (
                    {"tuple":("access_tokens.token", pymongo.DESCENDING),
                        "collection":"users",
                        "kwargs":{"unique":True}},
                    {"tuple":("username", pymongo.DESCENDING),
                        "collection":"users",
                        "kwargs":{"unique":True}},
                    {"tuple":("linked_accounts.id", pymongo.DESCENDING),
                        "collection":"users",
                        "kwargs":{"unique":True}},
                    {"tuple":("linked_accounts.type", pymongo.DESCENDING),
                        "collection":"users"}
                    )
            for idx in indexes:
                conn[settings["mongodb.db_name"]][idx["collection"]].create_index([idx["tuple"]],
                        **idx.get("kwargs", {}))

        create_indexes(conn)
        config.registry.settings['mongodb_conn'] = conn
        config.add_subscriber(add_mongo_db, NewRequest)

    def add_user(self, **kw):
        pass

    def add_group(self, whatever):
        pass

    def activate(self, token):
        pass

    def verify_access_token(self, token):
        pass
