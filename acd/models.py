import itertools

from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models import common, IdNameDescriptionMixin

from clld_cognacy_plugin.models import Cognateset
from clld_cognacy_plugin.interfaces import ICognateset


@implementer(interfaces.ILanguage)
class Variety(CustomModelMixin, common.Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    glottocode = Column(Unicode)
    group = Column(Unicode)
    is_proto = Column(Boolean)


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, common.Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    concepticon_id = Column(Unicode)


@implementer(ICognateset)
class Reconstruction(CustomModelMixin, Cognateset):
    pk = Column(Integer, ForeignKey('cognateset.pk'), primary_key=True)
    comment = Column(Unicode)
    proto_language = Column(Unicode)
    subset = Column(Integer)
    form_pk = Column(Integer, ForeignKey('value.pk'))
    form = relationship(common.Value)
    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(common.Language)
    implicit = Column(Boolean)

    etymon_pk = Column(Integer, ForeignKey('reconstruction.pk'))
    sets = relationship(
        'Reconstruction',
        order_by='Reconstruction.subset,Reconstruction.pk',
        foreign_keys=[etymon_pk],
        backref=backref('etymon', remote_side=[pk]))

    def grouped_sets(self):
        for ssid, sets in itertools.groupby(self.sets, lambda s: s.subset):
            if ssid:
                yield list(sets)

    def grouped_cognates(self):
        for grp, cogs in itertools.groupby(
            sorted(
                self.cognates,
                key=lambda c: (c.counterpart.valueset.language.group, -(c.counterpart.valueset.language.latitude or -180))),
            lambda c: c.counterpart.valueset.language.group,
        ):
            cs, l = [], None
            for c in cogs:
                cp = c.counterpart
                cs.append((
                    cp.valueset.language if cp.valueset.language != l else None,
                    cp,
                    cp.valueset.parameter.name.split('[')[0],
                ))
                l = cp.valueset.language
            yield grp, cs
