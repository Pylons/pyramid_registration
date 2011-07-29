from pyramid.config import Configurator
from pyramid_registration.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_view('pyramid_registration.views.my_view',
                    context='pyramid_registration:resources.Root',
                    renderer='pyramid_registration:templates/mytemplate.pt')
    config.add_static_view('static', 'pyramid_registration:static')
    return config.make_wsgi_app()

