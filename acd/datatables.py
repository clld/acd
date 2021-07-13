from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol
from clld.db.util import get_distinct_values

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
