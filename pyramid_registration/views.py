# lolreg.views package
# -------------------------------------------------------------

from pyramid.view import view_config

@view_config(route_name='lolreg.register')
def register_form(request):
    pass

@view_config(route_name='lolreg.activate')
def activate(request):
    request.context.activate(request.POST['token'])
