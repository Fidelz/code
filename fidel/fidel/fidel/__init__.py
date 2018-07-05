from pyramid.config import Configurator

from pyramid.session import SignedCookieSessionFactory

from sqlalchemy import engine_from_config

from .models import DBSession, Base

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)
    my_session_factory = SignedCookieSessionFactory('itsaseekreet')
    config.set_session_factory(my_session_factory)
    config.include('pyramid_jinja2')
    config.add_static_view(name='static', path='fidel:static')
    config.add_route('home', '/')
    config.add_route('add_zone', '/add_zone')
    config.add_route('show_zones', '/zones{barra:/?}{page:[0-9]*}')
    #config.add_route('show_zones', '/zones')
    config.add_route('delete_zone', '/zones/delete_zone')
    config.add_route('show_zone', '/zones/zone')
    config.add_route('search_zones', '/search_zones')
    config.scan()
    return config.make_wsgi_app()
