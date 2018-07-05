from pyramid.view import (
    view_config,
    view_defaults,
    notfound_view_config
    )
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.response import Response
import json
import os.path
from wtforms import Form, StringField, IntegerField, validators
from .models import DBSession, Zone

from paginate import Page

class AddZone(Form):
    acronym = StringField('Acronimo de la zona', [validators.InputRequired(), validators.Regexp("[a-z0-9-]+$")])
    polygon = StringField('Area de busqueda')

class IdZone(Form):
    id = IntegerField('id', [validators.InputRequired()])

class AcronymZone(Form):
    acronym = StringField('acronym', [validators.InputRequired(), validators.Regexp("[a-z]+$")])

class TutorialViews:
    def __init__(self, request):
        self.request = request

    @notfound_view_config()
    def notfound(request):
        return HTTPForbidden()

    @view_config(route_name='home', renderer='templates/home.jinja2')
    def home(self):
        form = AddZone()
        return {"form": form}

    @view_config(route_name='show_zones', renderer='templates/zones.jinja2')
    def show_zones(self):
        page = self.request.matchdict['page']
        zones = DBSession.query(Zone).order_by(Zone.dateadd.desc())
        per_page = 1
        p = Page(zones, page=page, items_per_page=per_page, item_count=zones.count())
        url = self.request.url
        url_rel = '$page'
        i = url.find("/zones") + 1
        if url[i:].find('/') == -1:
            url_rel = 'zones/' + url_rel
        pattern = '$link_first $link_previous ~4~ $link_next $link_last (Page $page our of $page_count - total $item_count)'
        pagination = p.pager(pattern, url=url_rel, dotdot_attr={'x':5}, link_attr={'y':6}, curpage_attr={'z':77})
        if page is "":
            page = 1
        index = (per_page * (int(page) -1))
        return {"zones": p, "pagination": pagination, "index": index}

    @view_config(route_name='search_zones', renderer='templates/zones.jinja2')
    def search_zones(self):
        request = self.request
        per_page = 5
        #page = request.matchdict['page']
        form = AcronymZone(request.GET)
        if request.method == 'GET' and form.validate():
            acronym = form.acronym.data
            zones = DBSession.query(Zone).filter(Zone.acronym.like("%"+acronym+"%")).\
                    order_by(Zone.dateadd.desc())
            page = 1 # CHANGE !!!!
            index = (per_page * (int(page) -1))
            # = Page(zones, page=page, items_per_page=per_page, item_count=zones.count())
            return {"zones": zones, "index": index}
        url = request.route_url('show_zones', page="1")
        return HTTPFound(location=url)

    @view_config(route_name='add_zone', renderer='templates/home.jinja2')
    def add_zone(self):
        request = self.request
        form = AddZone(request.POST)
        if request.method == 'POST' and form.validate():
            acronym = form.acronym.data
            polygon = form.polygon.data
            DBSession.add(Zone(acronym=acronym, polygon=polygon))
            return {"form": AddZone(), "result": "Zona guardada."}
        return {"form": AddZone(), "result": "Error al guardar la zona."}

    @view_config(route_name='show_zone', renderer='templates/zone.jinja2')
    def show_zone(self):
        request = self.request
        form = IdZone(request.GET)
        if request.method == 'GET' and form.validate():
            id = form.id.data
            zone = DBSession.query(Zone).filter_by(id=id)
            if zone.count() > 0:
                return {"zone": zone[0]}
        url = request.route_url('show_zones', page="1")
        return HTTPFound(location=url)

    @view_config(route_name='delete_zone')
    def delete_zone(self):
        request = self.request
        form = IdZone(request.GET)
        if request.method == 'GET' and form.validate():
            id = form.id.data
            zone = DBSession.query(Zone).filter_by(id=id)
            if zone.count() > 0:
                DBSession.query(Zone).filter_by(id=id).delete()
                url = request.route_url('show_zones', page="1")
                return HTTPFound(location=url)
        return Response('{"fail": "WRONG."}')
