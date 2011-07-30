import colander
import datetime
import pymongo
import random
import string

from pyramid.events import NewRequest
from pyramid_registration.interfaces import IRegistrationBackend
from zope.interface import implements

class AddUserSchema(colander.MappingSchema):
    regex = r'^[A-Za-z](?=[A-Za-z0-9_.]{3,31}$)[a-zA-Z0-9_]*\.?[a-zA-Z0-9_]*$'
    username = colander.SchemaNode(colander.String(),
        validator=colander.Regex(regex, msg="Use 4 to 32 characters and start with a letter. You may use letters, numbers, underscores, and one dot (.)"))

def _lookup_access_token(db, access_token):
    """ Check whether given token already exists in DB """
    return db.users.find_one({"access_tokens.token":access_token})

def _generate_access_token():
    """ Generate new access_token """
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))

def lookup_username(db, username):
    return db.users.find_one({"username":username})

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
            db_name = settings['mongodb.db_name']
            db = settings['mongodb_conn'][db_name]
            event.request.db = db
        conn = pymongo.Connection(db_uri)
        self.db = conn[settings["mongodb.db_name"]]
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

    def add_user(self, struct):
        """ Link an external account to this user """

        # may not exist
        user_doc = db.users.find_one({"linked_accounts.id":account_id})

        if user_doc:
            user_id = user_doc["_id"]
            username = user_doc["username"]
            # Has the account already been linked?
            if ({"id":account_id,"type":account_type} in
                    user_doc.get("linked_accounts", [])):
                return user_id
        else:
            user_id = ObjectId()
            username = make_temp_username(db)


        r = db.users.update({"_id":user_id},
                {
                    "$set":{
                        "suggested_username":suggested_username,
                        "username":username,
                        "first_name":first_name,
                        "last_name":last_name,
                    },
                    "$push":{
                        "linked_accounts":{"id":account_id, "type":account_type}
                    }
                },
            upsert=True, safe=True)
        if r.get("upserted"):
            user_id = r["upserted"]
        return user_id

    def activate(self, token):
        """ Mark account as activated. For simple auth (username & password)
        this may only follow email verification. For external auth e.g.
        Facebook Connect, Google OpenID, one may choose to trust the provider
        and automatically mark the account as activated. """
        self.db.users.update({"linked_accounts.token":token},
                {"$set":{"activated_timestamp":datetime.datetime.utcnow()}},
                safe=True)

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

