from pyramid.response import Response
""" Views """

def facebook_registration(backend, request):
    """ /registration/facebook view callable.
    
    If supplied with an access_token request parameter, assumes client has
    already performed the FB login dance.

    If not, sets upt the server-driven browser-redirect dance to authenticate
    use with FB.


    """
    pass

def facebook_login(backend, request):
    """ /login/facebook view callable.

    Takes a Facebook access token, checks for validity and if accepted 
    issues a usable token to client.
    """
    pass

def simple_registration(backend, request):
    """ /registration/simple view callable.

    Register a user with username and password.

    """
    username = request.params.get("username")
    password = request.params.get("password")
    email = request.params.get("email")

    if username and password and email:
        backend.add_user({"username":username,"password":password,"email":email})
        token = backend.issues_access_token

    return Response("foo")


def simple_login(backend, request):
    """ /login/simple view callable.

    Takes a username & password, checks for validity and if accepted 
    issues a usable token to client.
    """
    pass
