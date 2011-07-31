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
    """ Unit tests for MongoDBRegistrationBackend class. These do not talk to a
    real MongoDB server, instead mocking the PyMongo driver interactions. """

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
                    {"$set":{"access_tokens.$.activated_timestamp":utcnow}}, safe=True)

    @patch("pymongo.Connection")
    def test_issue_access_token(self, connection_mock):
        conn = connection_mock.instance()
        connection_mock.return_value = conn
        db = conn[self.settings["mongodb.db_name"]]
        backend = MongoDBRegistrationBackend(self.settings, self.config)

        uid = ObjectId()
        token = "token"
        with patch('pyramid_registration.mongodb._generate_access_token'):
            mongodb._generate_access_token.return_value = token
            def side_effect(*args):
                def second_call(*args):
                    return {"_id":uid}
                mongodb._generate_access_token.side_effect = second_call
                return None
            db.users.find_one.side_effect = side_effect
            backend.issue_access_token(uid)
            db.users.find_one.assert_called_with({"access_tokens.token":token})

    @patch("pymongo.Connection")
    def test_simple_login(self, connection_mock):
        conn = connection_mock.instance()
        connection_mock.return_value = conn
        db = conn[self.settings["mongodb.db_name"]]
        backend = MongoDBRegistrationBackend(self.settings, self.config)

        password = "testpassword"
        stored_user = {"username":"testuser",
                "password":_hash_pw("testpassword"),
                "email":"testemail@example.com"}

        # Test situation where user exists and we do password hash comparison
        db.users.find_one.return_value = stored_user
        self.assertTrue(backend.simple_login(stored_user["username"], password))

        # Test situation where user does not exist
        db.users.find_one.return_value = False
        self.assertFalse(backend.simple_login(stored_user["username"], password))

class MongoDBRegistrationBackendIntegrationTests(unittest.TestCase):
    """ Integration tests for MongoDBRegistrationBackend class. These talk to a
    real MongoDB server. """
    TEST_DB_NAME = "mongodbregtest"
    def setUp(self):
        from pyramid_registration import main
        self.config = testing.setUp()
        # XXX make configurable
        app = main({}, **{"mongodb.url":"mongodb://localhost",
            "mongodb.db_name":self.TEST_DB_NAME})
        from webtest import TestApp
        self.app = app
        self.testapp = TestApp(app)
        self.settings = app.registry.settings
        self.db = self.settings['mongodb_conn'][self.settings["mongodb.db_name"]]

    def tearDown(self):
        """ Clear out the application registry """
        testing.tearDown()
        self.settings["mongodb_conn"].drop_database(self.TEST_DB_NAME)

    def test_add_user(self):
        backend = MongoDBRegistrationBackend(self.settings, self.config)
        # Test good, available username, writing it to DB
        struct = {"username":"goodusername", "password":"password", "email":"testemail@example.com"}
        backend.add_user(struct)
        user_doc = self.db.users.find_one({"username":struct["username"]})
        self.assertEquals(user_doc["username"], struct["username"])
        self.assertEquals(user_doc["email"], struct["email"])
        self.assertNotEquals(user_doc["password"], struct["password"])
        # Test that we cannot add the same username again
        self.assertRaises(colander.Invalid, backend.add_user, struct)

    def test_activation(self):
        backend = MongoDBRegistrationBackend(self.settings, self.config)
        struct = {"username":"goodusername", "password":"password", "email":"testemail@example.com"}
        backend.add_user(struct)
        user_doc = self.db.users.find_one({"username":struct["username"]})
        self.assertEquals(user_doc["username"], struct["username"])
        self.assertEquals(user_doc["email"], struct["email"])
        self.assertNotEquals(user_doc["password"], struct["password"])

        # User has been added - verify it has no activated tokens
        for token in user_doc.get("access_tokens", []):
            self.assertFalse(token.get("activated_timestamp"))

        # Issue a token for this user
        access_token = backend.issue_access_token(user_doc["_id"])

        # Verify user has this access token in their user document
        user_doc = self.db.users.find_one({"username":struct["username"]})
        doc_token = False
        for token in user_doc.get("access_tokens", []):
            if token.get("token") == access_token:
                doc_token = token
                break

        self.assertEquals(doc_token["token"], access_token)
        # Verify this token is not activated
        self.assertFalse(doc_token.get("activated_timestamp"))
        # Ensure verify_access_token on this token returns False

        self.assertFalse(backend.verify_access_token(access_token))
        # Now activate the token, and assert that the token is marked as
        # activated in the database.
        backend.activate(access_token)

        user_doc = self.db.users.find_one({"username":struct["username"]})
        doc_token = False
        for token in user_doc.get("access_tokens", []):
            if token.get("token") == access_token:
                self.assertTrue(token.get("activated_timestamp"))
                break


        # Ensure verify_access_token on this token returns the user_id
        userid = backend.verify_access_token(access_token)
        self.assertEquals(userid, str(user_doc["_id"]))

    def test_simple_login(self):
        backend = MongoDBRegistrationBackend(self.settings, self.config)
        # Test good, available username, writing it to DB
        password = "testpassword"
        struct = {"username":"goodusername", "password":password, "email":"testemail@example.com"}
        backend.add_user(struct)
        # Now lets verify we can retrieve it correctly with a simple_login
        user_doc = backend.simple_login(struct["username"], struct["password"])
        self.assertEquals(struct["username"], user_doc["username"])
        self.assertEquals(struct["email"], user_doc["email"])
        # Same again but by email not username
        user_doc = backend.simple_login(struct["email"], struct["password"])
        self.assertEquals(struct["username"], user_doc["username"])
        self.assertEquals(struct["email"], user_doc["email"])
        # Failure case: bad password
        user_doc = backend.simple_login(struct["email"], "wrongpassword")
        self.assertFalse(user_doc)




class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

