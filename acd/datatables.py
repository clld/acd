from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol

from clld_glottologfamily_plugin.models import Family
from clld_glottologfamily_plugin.datatables import FamilyCol
from clld_cognacy_plugin.datatables import Cognatesets

from acd import models


class Languages(datatables.Languages):
    def base_query(self, query):
        return query.join(Family).options(joinedload(models.Variety.family)).distinct()

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            FamilyCol(self, 'Family', models.Variety),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
            LinkToMapCol(self, 'm'),
        ]


class Etyma(Cognatesets):
    def base_query(self, query):
        return Cognatesets.base_query(self, query).filter(models.Reconstruction.etymon_pk == None)

    def col_defs(self):
        return [
            Col(self, 'PLg', model_col=models.Reconstruction.proto_language),
            LinkCol(self, 'name', sTitle='form'),
            Col(self, 'description')
        ]


def includeme(config):
    config.register_datatable('languages', Languages)
