from zope.interface import Interface

class IRegistrationBackend(Interface):

    def add_user(self, **kw):
        """ Add a user to the storage
        TODO: define params """

    def add_group(self, whatever):
        """ Add a group to the storage
        TODO: define params """

    def activate(self, token):
        """ Mark user as activated.
        TODO: define params """

    def verify_access_token(self, token):
        """ Verify access token
        Return the user object if valid,
        None otherwise. """
