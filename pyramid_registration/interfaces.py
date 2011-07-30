from zope.interface import Interface

class IRegistrationBackend(Interface):

    def __init__(self, config, settings):
        """ Must pass in configurator and settings objects

        ``config``
        An instance of :class:`pyramid.config.Configurator`

        ``settings``
        An instance of :class:`pyramid.settings.Settings`
        """

    def add_user(self, struct):
        """ Add a user to the storage.

        ``struct``
        User structure to store. It is up to the backend implementation to
        validate this structure. However, it is probably safe to assume it
        supports keys username, password and email.
        """

    def activate(self, token):
        """ Mark user as activated.

        ``token``
        The token linked to the account to activate. """

    def verify_access_token(self, token):
        """ Verify whether access token is associated with a valid account and is not

        ``token``
        The token to verify.

        Returns the user id if valid, None otherwise. """

    def issue_access_token(self, user_id):
        """ Generate a new random access token
        and associate it with the user_id in the database.

        ``user_id``
        The user_id of the account to issue the token for.
        """
