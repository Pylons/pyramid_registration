from pyramid.config import Configurator
from pyramid_registration.resources import Root
from pyramid_registration.auth_policy import PyramidRegistrationAuthenticationPolicy
from pyramid_registration.views import facebook_registration, facebook_login, simple_registration, simple_login

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_static_view('static', 'pyramid_registration:static')
    backend_factory = settings.get('pyramid_registration.backend_factory',
                                   'pyramid_registration.mongodb.MongoDBRegistrationBackend')
    backend_factory = config.maybe_dotted(backend_factory)
    backend = backend_factory(settings)
    # Seems standard to keep "Registration" and "Login" separate, although
    # with external auth providers (e.g. Facebook) this isn't stricly necessary.
    # "Registration" is to create a new account.
    # "Login" is to exchange some credentials for a valid access token
    config.add_route('facebook_registration', '/registration/facebook', factory=backend)
    config.add_route('facebook_login', '/login/facebook', factory=backend)
    config.add_route('simple_registration', '/registration/simple', factory=backend)
    ronfig.add_route('simple_login', '/login/simple', factory=backend)
    config.add_view(facebook_registration, 'facebook_registration')
    config.add_view(simple_registration, 'simple_registration')
    config.add_view(facebook_login, 'facebook_login')
    config.add_view(simple_login, 'simple_login')
    config.set_authentication_policy(PyramidRegistrationAuthenticationPolicy(backend))

    return config.make_wsgi_app()

