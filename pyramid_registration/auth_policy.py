from pyramid.interfaces import IAuthenticationPolicy
from zope.interface import implements

class PyramidRegAuthenticationPolicy(object):
    implements(IAuthenticationPolicy)
    def __init__(self, backend):
        self.backend = backend

    def authenticated_userid(self, request):
        # use self.backend to figure out who the guy is and if he exists
        pass

    # ..  other IAuthenticationPolicy methods ...
