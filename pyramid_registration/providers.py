import json
import urllib

def facebook_provider(fb_access_token):
    """ Performs a Facebook Graph API request for user "me" with the supplied
    access token. On success, the decoded JSON response is returned. On failure,
    False is returned.

    ``fb_access_token``
    A Facebook Graph API access token.
    """
    base_url = "https://graph.facebook.com/me"
    q = urllib.urlencode({"access_token":fb_access_token})

    f = urllib.urlopen("%s?%s"%(base_url, q))
    data = f.read()
    body = json.loads(data)
    if body["error"]:
        return False
    return body

def google_provider(google_access_token):
    """ Performs a Google OAuth2 API request with minimal scope (enough to get
    email address). On success, the decoded JSON response is returned. On
    failure, False is returned.
    See https://sites.google.com/site/oauthgoog/Home/emaildisplayscope

    ``google_access_token``
    A Google OAuth2 access token.
    """
    pass

