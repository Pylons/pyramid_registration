from zope.interface import implements

from pyramid_registration.interfaces import IRegistrationBackend

class MongoDBRegistrationBackend(object):
    """ MongoDB implementation of RegistrationBackend """
    implements(IRegistrationBackend)

    def __init__(self, settings):
        pass

    def add_user(self, **kw):
        pass

    def add_group(self, whatever):
        pass

    def activate(self, token):
        pass

    def verify_access_token(self, token):
        pass
