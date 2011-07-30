import colander
import datetime
import json
import mongodb
import pyramid.config
import pyramid.registry
import pymongo
import os
import unittest

from mongodb import MongoDBRegistrationBackend, _hash_pw, _check_pw

from pymongo.objectid import ObjectId
from mock import Mock, patch


from pyramid import testing

class MongoDBRegistrationBackendUnitTests(unittest.TestCase):
    """ Unit tests for MongoDBRegistrationBackend class """

    def setUp(self):
        self.settings = {"mongodb.url":"mongodb://localhost",
                "mongodb.db_name":"testdb"}
        self.config = Mock(spec=pyramid.config.Configurator)
        self.config.registry = Mock(spec=pyramid.registry.Registry)
        self.config.registry.settings = {}

    def tearDown(self):
        testing.tearDown()

    @patch("pymongo.Connection")
    def test_init(self, connection_mock):
        conn = connection_mock.instance()
        connection_mock.return_value = conn
        backend = MongoDBRegistrationBackend(self.settings, self.config)

        self.assertEquals(self.config.registry.settings["mongodb_conn"], conn)
        self.assertEquals(backend.db, conn[self.settings["mongodb.db_name"]])

    def test_password_hash(self):
        p = "password"
        h = _hash_pw(p)
        self.assertTrue(_check_pw(p, h))

    @patch("pymongo.Connection")
    def test_add_user(self, connection_mock):
        # Test bad username
        struct = {"username":"BAD"}
        conn = connection_mock.instance()
        connection_mock.return_value = conn
        db = conn[self.settings["mongodb.db_name"]]
        backend = MongoDBRegistrationBackend(self.settings, self.config)
        self.assertRaises(colander.Invalid, backend.add_user, struct)
        # Test good username that already exists in DB
        struct["username"] = "good"
        db.users.find_one.return_value = {"username":struct["username"]}
        self.assertRaises(colander.Invalid, backend.add_user, struct)
        # Test good, available username, writing it to DB
        db.users.find_one.return_value = None
        backend.add_user(struct)
        db.users.insert.assert_called_once_with({"username":struct["username"]},
                safe=True)
        # Test writing bcrypted password value to DB
        struct["password"] = "testpassword"
        hashed_pw = _hash_pw(struct["password"])
        # patch bcrypt module to return the hash we just generated
        with patch("pyramid_registration.mongodb.bcrypt.hashpw"):
            mongodb.bcrypt.hashpw.return_value = hashed_pw
            backend.add_user(struct)
            db.users.insert.assert_called_with({"username":struct["username"],"password":hashed_pw},
                    safe=True)
        # Test writing email to DB
        struct["email"] = "testemail@example.com"
        del struct["password"]
        backend.add_user(struct)
        db.users.insert.assert_called_with({"username":struct["username"],"email":struct["email"]},
                safe=True)

    @patch("pymongo.Connection")
    def test_verify_access_token(self, connection_mock):
        conn = connection_mock.instance()
        connection_mock.return_value = conn
        db = conn[self.settings["mongodb.db_name"]]
        backend = MongoDBRegistrationBackend(self.settings, self.config)

        # Test that a non-existant token will not verify
        db.users.find_one.return_value = None
        self.assertFalse(backend.verify_access_token("token"))

        # Test that a matching token will return a stringified ID
        with patch("pyramid_registration.mongodb._purge_old_tokens"):

            oid = ObjectId()
            db.users.find_one.return_value = {"_id":oid}
            self.assertEquals(backend.verify_access_token("token"), str(oid))

            # Test that verify has tried to purge the expired tokens
            mongodb._purge_old_tokens.assert_called_once_with(db, oid)

    @patch("pymongo.Connection")
    def test_activate(self, connection_mock):
        conn = connection_mock.instance()
        connection_mock.return_value = conn
        db = conn[self.settings["mongodb.db_name"]]
        backend = MongoDBRegistrationBackend(self.settings, self.config)
        utcnow = datetime.datetime.utcnow()
        with patch('datetime.datetime'):
            datetime.datetime.utcnow.return_value = utcnow
            backend.activate("token")
            db.users.update.assert_called_once_with({"access_tokens.token":"token"},
                    {"$set":{"activated_timestamp":utcnow}}, safe=True)





class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()



class IntegrationTests(unittest.TestCase):
    def setUp(self):
        from pyramid_registration import main
        # XXX make configurable
        app = main({}, **{"mongodb.url":"mongodb://localhost",
            "mongodb.db_name":test_db,
            "mako.directories":"dragpushpullcom:templates"})
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.settings = app.registry.settings
        self.db = self.settings['mongodb_conn'][self.settings["mongodb.db_name"]]

    def tearDown(self):
        """ Clear out the application registry """
        testing.tearDown()
        self.settings["mongodb_conn"].drop_database(test_db)
