from pyramid.config import Configurator

from pyramid.session import SignedCookieSessionFactory
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

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
    authn_policy = AuthTktAuthenticationPolicy(settings['fidel.secret'],
                                               hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_jinja2')
    config.add_static_view(name='static', path='fidel:static')
    config.add_route('home', '/')
    config.add_route('admin', '/admin')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('create_user', '/create_user')
    config.add_route('add_user', '/add_user')
    config.add_route('map_zones', '/map_zones')
    config.add_route('map_propierties', '/map_propierties')
    config.add_route('add_zone', '/add_zone')
    config.add_route('show_zones', '/zones{barra:/?}{page:[0-9]*}')
    config.add_route('delete_zone', '/zones/delete_zone')
    config.add_route('show_zone', '/zones/zone')
    config.scan()
    return config.make_wsgi_app()
