from sqlalchemy import func
from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol, DataTable
from clld.db.util import get_distinct_values
from clld.db.meta import DBSession
from clld.db.models import common

from clld_cognacy_plugin.datatables import Cognatesets

from acd import models


class Languages(datatables.Languages):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            Col(self,
                'group',
                model_col=models.Variety.group,
                choices=get_distinct_values(models.Variety.group)),
            Col(self,
                'proto',
                model_col=models.Variety.is_proto),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
            LinkToMapCol(self, 'm'),
        ]


class FtsCol(Col):
    __kw__ = dict(
        bSortable=False,
        sTitle='Gloss',
        sDescription='')

    def format(self, item):
        return item.description

    def search(self, qs):
        # sanitize, normalize, and & (AND) the resulting stems
        # see also https://bitbucket.org/zzzeek/sqlalchemy/issues/3160/postgresql-to_tsquery-docs-and
        query = func.plainto_tsquery('english', qs)
        return self.model_col.op('@@')(query)


class Etyma(Cognatesets):
    def base_query(self, query):
        return Cognatesets.base_query(self, query).filter(models.Reconstruction.etymon_pk == None)

    def col_defs(self):
        return [
            Col(self, 'PLg', model_col=models.Reconstruction.proto_language),
            LinkCol(self, 'name', sTitle='form'),
            #Col(self, 'description'),
            FtsCol(self, 'gloss', model_col=models.Reconstruction.gloss)
        ]


class Formsets(DataTable):
    __constraints__ = [common.Contribution]

    def base_query(self, query):
        return DBSession.query(models.Formset).filter(models.Formset.contribution == self.contribution)

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
        ]


def includeme(config):
    config.register_datatable('languages', Languages)
    config.register_datatable('formsets', Formsets)
