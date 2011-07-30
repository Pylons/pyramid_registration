""" Views """

def facebook_registration(request):
    """ /registration/facebook view callable.
    
    If supplied with an access_token request parameter, assumes client has
    already performed the FB login dance.

    If not, sets upt the server-driven browser-redirect dance to authenticate
    use with FB.


    """
    pass

def facebook_login(request):
    """ /login/facebook view callable.

    Takes a Facebook access token, checks for validity and if accepted 
    issues a usable token to client.
    """

def simple_registration(request):
    """ /registration/simple view callable.

    Register a user with username and password.

    TODO: Also collect email by default?
    """
    pass


def simple_login(request):
    """ /login/simple view callable.

    Takes a username & password, checks for validity and if accepted 
    issues a usable token to client.
    """
