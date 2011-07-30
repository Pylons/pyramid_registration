import datetime
import pymongo
import random

from pyramid.events import subscriber
from pyramid.events import NewRequest
from pymongo.son import SON

from zope.interface import implements
from pyramid_registration.interfaces import IRegistrationBackend

class MongoDBUser(SON):

    def get_id(self):
        return self["_id"]


def _lookup_access_token(db, access_token):
    """ Check whether given token already exists in DB """
    return db.users.find_one({"access_tokens.token":access_token},
            as_class=MongoDBUser)

def _generate_access_token():
    """ Generate new access_token """
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))

def lookup_username(db, username):
    return db.users.find_one({"username":username}, as_class=MongoDBUser)

def _generate_temp_username():
    """ Generate a temporary username """
    return "user%d" % random.randint(0, 99999999)

def _purge_old_tokens(db, user_id, timedelta=None):
    # pull any tokens older than timedelta.
    if not timedelta:
        timedelta = datetime.timedelta(days=30)
    expiry = datetime.datetime.utcnow() - timedelta
    db.users.update({"_id":user_id},
            {"$pull":{
                "access_tokens":
                    {"timestamp":
                        {"$lte":expiry}
                    }
                }
            },
            safe=True)

def _store_access_token(db, user_id, token):
    """ Store given access_token in DB. Purge any older than 30 days.
    Note: May be race conditions """

    _purge_old_tokens(db, user_id)

    # Push the new token
    db.users.update({"_id":user_id},
            {"$push":
                {"access_tokens":
                    {"token":token,"timestamp":datetime.datetime.utcnow()}
                }
            },
            safe=True)

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
        self.db = settings["mongodb_conn"][settings["mongodb.db_name"]]
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
        """ Purge expired tokens for this user, then look up against current tokens
        to check validity """
        user_doc = _lookup_access_token(self.db, token)
        if not user_doc: return None
        _purge_old_tokens(self.db, user_doc["_id"])

        user_doc = _lookup_access_token(self.db, token)
        if user_doc:
            return str(user_doc["_id"])
        return None


    def issue_access_token(self, user_id):
        """ Create a unique access_token and associate it with the user in the DB,
        returning resulting string """

        # XXX potential race between checking & generation, but very unlikely to
        # ever hit. Note, we do have a unique index on token, so this should at
        # worst throw an exception, not actually end up with duplicates
        while True:
            token = _generate_access_token()
            if not _lookup_access_token(self.db, token): break
        _store_access_token(self.db, user_id, token)

        return token

