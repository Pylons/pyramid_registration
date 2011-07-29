# user app
# -------------------------------------------------------------

from pyramid.config import Configurator
from pyramid.view import view_config

@view_config(route_name='lolreg.register')
def my_register_form(request):
    # self-posting form
    pass

@view_config(route_name='lolreg.activate')
def my_activate(request):
    pass

if __name__ == '__main__':
    config = Configurator()
    config.include('lolreg', route_prefix='/registration')

    # accept default views
    config.scan('lolreg.views')

    # or use your own views

    # config.scan('__main__')

    # or use default views then customize some

    # config.scan('lolreg.views')
    # config.commit()
    # config.add_view(my_register_form, route_name='lolreg.register')

