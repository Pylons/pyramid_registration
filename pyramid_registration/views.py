import colander
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

def simple_registration_get(backend, request):
    """ /registration/simple view callable for GET method.
    Renders registration template.
    """
    return {"errors":[], "created":False}

def simple_registration_post(backend, request):
    """ /registration/simple view callable for POST method.

    Register a user with username and password.

    """
    # XXX move to deform
    username = request.params.get("username", "")
    password = request.params.get("password", "")
    password_confirm = request.params.get("password-confirm", "")
    email = request.params.get("email", "")

    errors = []
    if password != password_confirm:
        errors.append("Password and password confirm do not match")
    if not password or not password_confirm:
        errors.append("Must supply a password")
    if not email:
        errors.append("Must supply an email")
    try:
        backend.add_user({"username":username,"password":password,"email":email})
    except colander.Invalid, e:
        for i in e:
            if isinstance(i, unicode) or isinstance(i, str):
                errors.append(i)
    if not errors:
        return {"errors":errors, "created":True}

    return {"errors":errors, "created":False}


def simple_login_post(backend, request):
    """ /login/simple view callable for POST method requests.

    Takes a username & password, checks for validity and if accepted
    issues a usable token to client.
    """
    username = request.params.get("username")
    password = request.params.get("password")


    if backend.simple_login(username, password):
        token = backend.issue_access_token()
        # set header, optionally redirect
        return
    # login failure
    return

def simple_login_get(backend, request):
    """ /login/simple view callable for GET method requests.

    Renders the login form.
    """
    return

