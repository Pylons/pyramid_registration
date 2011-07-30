from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Authenticated, Everyone
from zope.interface import implements

class PyramidRegistrationAuthenticationPolicy(object):
    implements(IAuthenticationPolicy)
    def __init__(self, backend):
        self.backend = backend

    def unauthenticated_userid(self, request):
        return request.params.get("access_token")

    def authenticated_userid(self, request):
        # use self.backend to figure out who the guy is and if he exists
        access_token = self.unauthenticated_userid(request)
        user_obj = self.backend.verify_access_token(access_token)
        if not user_obj: return None
        return user_obj.get_id()

    def remember(self, request, principal, **kw):
        """ No-Op """
        pass

    def forget(self, request):
        """ No-Op """
        pass

    def effective_principals(self, request):
        principals = [Everyone]
        uid = self.authenticated_userid(request)
        if uid:
            principals += [Authenticated, "u:%s" % str(uid)]
        return principals
