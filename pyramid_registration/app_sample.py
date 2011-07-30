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
