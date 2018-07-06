from pyramid.view import (
    view_config,
    view_defaults,
    notfound_view_config
    )
from pyramid.security import (
    remember,
    forget,
    )

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.response import Response
import json
import os.path
from wtforms import Form, StringField, IntegerField, PasswordField, FloatField, validators
from .models import DBSession, Zone, Property, UserLogin

from paginate import Page

from sqlalchemy import exc


class AddZone(Form):
    acronym = StringField('Acronimo de la zona', [validators.InputRequired(),
                          validators.Regexp("[a-z0-9-]+$")])
    polygon = StringField('Area de busqueda')

class AddProperty(Form):
    acronym = StringField('Acronimo de la propiedad', [validators.InputRequired(),
                          validators.Regexp("[a-z0-9-]+$")])
    lat = FloatField('Latitud')
    long = FloatField('Longitud')

class Login(Form):
    username = StringField('Usuario', [validators.InputRequired(),
                           validators.Regexp("[A-Za-z0-9-_]+$")])
    password = PasswordField('Contraseña', [validators.InputRequired()])


class IdZone(Form):
    id = IntegerField('id', [validators.InputRequired()])


class AcronymZone(Form):
    acronym = StringField('acronym', [validators.InputRequired(),
                          validators.Regexp("[a-z]+$")])


class Views:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid

    @notfound_view_config()
    def notfound(request):
        return HTTPForbidden()

    @view_config(route_name='home', renderer='templates/home.jinja2')
    def home(self):
        form = Login()
        return {"form": form, "result": self._get_result_form()}

    @view_config(route_name='login')
    def login(self):
        request = self.request
        form = Login(request.POST)
        if request.method == 'POST' and form.validate():
            username = form.username.data
            password = form.password.data
            query = DBSession.query(UserLogin).filter_by(username=username,
                                                         password=password)
            correct_login = query.count()
            if correct_login:
                headers = remember(request, username)
                url = request.route_url('admin')
                return HTTPFound(location=url, headers=headers)
        request.session.flash("Error: los datos no son correctos.")
        url = request.route_url('home')
        return HTTPFound(location=url)

    @view_config(route_name='logout')
    def logout(self):
        self._check_session()
        request = self.request
        headers = forget(request)
        url = request.route_url('home')
        return HTTPFound(location=url, headers=headers)

    @view_config(route_name='admin', renderer='templates/admin.jinja2')
    def admin(self):
        self._check_session()
        result = self._get_result_form()
        return {"result": result}

    @view_config(route_name='create_user',
                 renderer='templates/createuser.jinja2')
    def create_user(self):
        self._check_session()
        form = Login()
        result = self._get_result_form()
        return {"form": form, "result": result}

    @view_config(route_name='add_user')
    def add_user(self):
        self._check_session()
        request = self.request
        form = Login(request.POST)
        url = request.route_url('create_user')
        if request.method == 'POST' and form.validate():
            username = form.username.data
            password = form.password.data
            try:  # username must be unique
                DBSession.add(UserLogin(username=username, password=password))
                DBSession.flush()
                request.session.flash("Usuario creado correctamente.")
                url = request.route_url('admin')
            except exc.IntegrityError:
                DBSession.rollback()
                request.session.flash("Error: el usuario ya existe.")
        else:
            request.session.flash("Error: los datos introducidos no" +
                                  " son correctos.")
        return HTTPFound(location=url)

    @view_config(route_name='map_zones', renderer='templates/mapzones.jinja2')
    def map_zones(self):
        self._check_session()
        form = AddZone()
        result = self._get_result_form()
        return {"form": form, "result": result}

    @view_config(route_name='map_propierties', renderer='templates/mappropierties.jinja2')
    def map_propierties(self):
        self._check_session()
        form = AddProperty()
        result = self._get_result_form()
        return {"form": form, "result": result}

    @view_config(route_name='show_zones', renderer='templates/zones.jinja2')
    def show_zones(self):
        self._check_session()
        request = self.request
        per_page = 2
        page = self._get_page()
        form = AcronymZone(request.GET)
        index = (per_page * (page - 1))
        pattern = '$link_first $link_previous ~4~ $link_next $link_last' + \
                  '(Pagina $page de $page_count - zonas totales $item_count)'
        if request.method == 'GET' and form.validate():
            return self._search_zones(form.acronym.data, page, per_page, index,
                                      pattern)
        else:
            zones = DBSession.query(Zone).order_by(Zone.dateadd.desc())
            url_rel = '$page'
            return self._paginate_zones(zones, page, per_page, request.url,
                                        url_rel, pattern, index)

    def _search_zones(self, acronym, page, per_page, index, pattern):
        zones = DBSession.query(Zone).filter(Zone.acronym.
                                             like("%"+acronym+"%")).\
                                             order_by(Zone.dateadd.desc())
        url_rel = '$page?acronym=' + acronym
        return self._paginate_zones(zones, page, per_page, self.request.url,
                                    url_rel, pattern, index)

    def _paginate_zones(self, zones, page, per_page, url, url_rel, pattern,
                        index):
        p = Page(zones, page=page, items_per_page=per_page,
                 item_count=zones.count())
        i = url.find("/zones") + 1
        link_add_delete = ""
        if url[i:].find('/') == -1:
            url_rel = 'zones/' + url_rel
            link_add_delete = 'zones/'
        pagination = p.pager(pattern, url=url_rel, dotdot_attr={'x': 5},
                             link_attr={'y': 6}, curpage_attr={'z': 77})
        return {"zones": p, "pagination": pagination, "index": index,
                "link_add_delete": link_add_delete}

    def _get_page(self):
        page = self.request.matchdict['page']
        if page is "":
            page = 1
        return int(page)

    @view_config(route_name='add_zone')
    def add_zone(self):
        self._check_session()
        request = self.request
        form = AddZone(request.POST)
        url = request.route_url('map_zones')
        if request.method == 'POST' and form.validate():
            acronym = form.acronym.data
            polygon = form.polygon.data
            DBSession.add(Zone(acronym=acronym, polygon=polygon))
            request.session.flash("Zona guardada.")
            return HTTPFound(location=url)
        request.session.flash("Error al guardar la zona.")
        return HTTPFound(location=url)

    @view_config(route_name='show_zone', renderer='templates/zone.jinja2')
    def show_zone(self):
        self._check_session()
        request = self.request
        form = IdZone(request.GET)
        if request.method == 'GET' and form.validate():
            id = form.id.data
            zone = DBSession.query(Zone).filter_by(id=id)
            if zone.count() > 0:
                return {"zone": zone[0]}
        url = request.route_url('show_zones', barra="/", page="1")
        return HTTPFound(location=url)

    @view_config(route_name='delete_zone')
    def delete_zone(self):
        self._check_session()
        request = self.request
        form = IdZone(request.GET)
        if request.method == 'GET' and form.validate():
            id = form.id.data
            zone = DBSession.query(Zone).filter_by(id=id)
            if zone.count() > 0:
                DBSession.query(Zone).filter_by(id=id).delete()
                url = request.route_url('show_zones', barra="/", page="1")
                return HTTPFound(location=url)
        url = request.route_url('show_zones', barra="/", page="1")
        return HTTPFound(location=url)

    def _get_result_form(self):
        result = self.request.session.pop_flash()
        if not result:
            result = ""
        else:
            result = result[0]
        return result

    def _check_session(self):
        if not self.logged_in:
            raise HTTPForbidden()
