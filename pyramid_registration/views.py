import colander
import deform
from mongodb import AddUserSchema, email_validator
from pyramid.response import Response

class SignupSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), validator=email_validator,
            widget=deform.widget.TextInputWidget(size=20))
    password = colander.SchemaNode(colander.String(),
            validator=colander.Length(min=6),
            widget=deform.widget.PasswordWidget(size=20))

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
    schema = SignupSchema()
    form = deform.Form(schema, buttons=('create',))
    return {"form":form.render()}

def simple_registration_post(backend, request):
    """ /registration/simple view callable for POST method.

    Register a user with username and password.

    """
    controls = request.POST.items()
    try:
        schema = SignupSchema()
        form = deform.Form(schema, buttons=('submit',))
        form.validate(controls)
        schema.bind(db=request.db, email=request.POST.get("email"))
        d = schema.deserialize(request.POST)
        backend.add_user({"password":d["password"], "email":d["email"]})
    except deform.ValidationFailure, e:
        return {'form':e.render()}
    return {'form':'OK'}

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

