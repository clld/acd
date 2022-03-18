from sqlalchemy import func
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol, DataTable, DetailsRowLinkCol
from clld.web.datatables.value import Values
from clld.db.util import get_distinct_values, contains
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


class FormCol(LinkCol):
    __kw__ = dict(sDescription='You may type <emph>ny</emph> for <emph>ñ</emph> and '
                               '<emph>ng</emph> for <emph>ŋ</emph>.')

    def search(self, qs):
        return contains(self.model_col, qs.replace('ny', 'ñ').replace('ng', 'ŋ'))


class Etyma(Cognatesets):
    # Note: registered in main function!
    def base_query(self, query):
        return Cognatesets.base_query(self, query).filter(models.Reconstruction.etymon_pk == None)

    def col_defs(self):
        return [
            Col(self,
                'PLg',
                model_col=models.Reconstruction.proto_language,
                choices=get_distinct_values(models.Reconstruction.proto_language)),
            FormCol(self, 'name', sTitle='form'),
            Col(self, 'initial', input_size='mini', model_col=models.Reconstruction.form_initials),
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


class Forms(Values):
    def col_defs(self):
        if self.language:
            return [
                Col(self, 'name', sTitle='Form'),
                LinkCol(
                    self,
                    'Meaning',
                    get_object=lambda i: i.valueset.parameter,
                    model_col=common.Parameter.name),
                DetailsRowLinkCol(self, 'd', button_text='show set', sTitle='Cognate set'),
            ]
        return Values.col_defs(self)


def includeme(config):
    config.register_datatable('languages', Languages)
    config.register_datatable('formsets', Formsets)
    config.register_datatable('values', Forms)
