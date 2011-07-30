import datetime
import json
import pymongo
import os
import unittest

from pymongo.objectid import ObjectId
from mock import patch


from pyramid import testing

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
