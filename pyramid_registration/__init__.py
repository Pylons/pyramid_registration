from pyramid.config import Configurator
from pyramid_registration.resources import Root
from pyramid_registration.auth_policy import PyramidRegistrationAuthenticationPolicy
from pyramid_registration.views import facebook_registration, facebook_login, simple_registration_post, simple_registration_get, simple_login_post, simple_login_get

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_static_view('static', 'pyramid_registration:static')
    backend_factory = settings.get('pyramid_registration.backend_factory',
                                   'pyramid_registration.mongodb.MongoDBRegistrationBackend')
    backend_factory = config.maybe_dotted(backend_factory)
    backend = backend_factory(settings, config)
    # Seems standard to keep "Registration" and "Login" separate, although
    # with external auth providers (e.g. Facebook) this isn't stricly necessary.
    # "Registration" is to create a new account.
    # "Login" is to exchange some credentials for a valid access token
    config.add_route('facebook_registration', '/registration/facebook',
            view=facebook_registration, factory=backend)
    config.add_route('facebook_login', '/login/facebook', view=facebook_login, factory=backend)
    config.add_route('simple_registration_post', '/registration/simple',
            view=simple_registration_post, factory=backend,
            renderer="pyramid_registration:templates/simple_reg.mak",
            request_method="POST")
    config.add_route('simple_registration_get', '/registration/simple',
            view=simple_registration_get, factory=backend,
            renderer="pyramid_registration:templates/simple_reg.mak",
            request_method="GET")
    config.add_route('simple_login_post', '/login/simple', view=simple_login_post,
            factory=backend, request_method="POST")
    config.add_route('simple_login_get', '/login/simple', view=simple_login_get,
            factory=backend, request_method="GET")
    # XXX _set_authentication_policy will be made public as
    # set_authentication_policy soon.
    config._set_authentication_policy(PyramidRegistrationAuthenticationPolicy(backend))

    return config.make_wsgi_app()

