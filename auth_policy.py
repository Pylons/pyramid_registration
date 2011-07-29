# lolreg package
# -------------------------------------------------------------
from pyramid.interfaces import IAuthenticationPolicy
from zope.interface import implements

class LolRegAuthenticationPolicy(object):
    implements(IAuthenticationPolicy)
    def __init__(self, backend):
        self.backend = backend

    def authenticated_userid(self, request):
        # use self.backend to figure out who the guy is and if he exists
        pass

    # ..  other IAuthenticationPolicy methods ...

def includeme(config):
    settings = config.settings
    backend_factory = settings.get('lolreg.backend_factory',
                                   'lolreg.sqla.SQLARegistrationBackend')
    backend_factory = config.maybe_dotted(backend_factory)
    backend = backend_factory(settings)
    config.add_route('lolreg.register', '/register', factory=backend)
    config.add_route('lolreg.activate', '/activate', factory=backend)
    config.set_authentication_policy(LolRegAuthenticationPolicy(backend))
