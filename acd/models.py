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
from sqlalchemy.dialects.postgresql import TSVECTOR

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models import common, IdNameDescriptionMixin

from clld_cognacy_plugin.models import Cognateset
from clld_cognacy_plugin.interfaces import ICognateset

from acd.interfaces import IFormset


def group_counterparts(iterable):
    for grp, cogs in itertools.groupby(
            sorted(
            iterable,
                key=lambda c: (
                        c.counterpart.valueset.language.group, -(c.counterpart.valueset.language.latitude or -180))),
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


#
# FIXME: what to do with Near, Noise and Loan -> IFormSet
#
@implementer(IFormset)
class Formset(Base, IdNameDescriptionMixin):
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contribution = relationship(common.Contribution, backref='formsets')
    comment = Column(Unicode)
    # dempwolff_reconstruction

    def grouped_forms(self):
        yield from group_counterparts(self.members)


class Member(Base):
    """
    The association table between counterparts for concepts in particular languages and
    cognate sets.
    """
    formset_pk = Column(Integer, ForeignKey('formset.pk'))
    formset = relationship(Formset, backref='members')
    counterpart_pk = Column(Integer, ForeignKey('value.pk'))
    counterpart = relationship(common.Value, backref='memberships')


@implementer(interfaces.IValue)
class Form(CustomModelMixin, common.Value):
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)

    def iter_explicit_reconstructions(self):
        seen = set()
        for cog in self.cognates:
            if cog.cognateset.etymon:
                if cog.cognateset.implicit:
                    if cog.cognateset.explicit.id not in seen:
                        yield cog.cognateset.explicit
                        seen.add(cog.cognateset.explicit.id)
                else:
                    if cog.cognateset.id not in seen:
                        yield cog.cognateset
                        seen.add(cog.cognateset.id)

    def grouped_formsets(self):
        for _, memberships in itertools.groupby(
            sorted(self.memberships, key=lambda mm: mm.formset.contribution_pk),
            lambda mm: mm.formset.contribution_pk,
        ):
            formsets = [m.formset for m in memberships]
            yield formsets[0].contribution, formsets


@implementer(interfaces.ILanguage)
class Variety(CustomModelMixin, common.Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    glottocode = Column(Unicode)
    group = Column(Unicode)
    is_proto = Column(Boolean)
    parent_language = Column(Unicode)


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, common.Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    concepticon_id = Column(Unicode)

    @property
    def label(self):
        return self.name.split('[')[0].strip()


class ReconstructionRelation(Base):
    source_pk = Column(Integer, ForeignKey('reconstruction.pk'))
    target_pk = Column(Integer, ForeignKey('reconstruction.pk'))
    type = Column(Unicode)


@implementer(ICognateset)
class Reconstruction(CustomModelMixin, Cognateset):
    pk = Column(Integer, ForeignKey('cognateset.pk'), primary_key=True)
    gloss = Column(TSVECTOR)
    comment = Column(Unicode)
    proto_language = Column(Unicode)
    subset = Column(Integer)
    form_pk = Column(Integer, ForeignKey('value.pk'))
    form = relationship(common.Value, backref=backref('reconstruction', uselist=False))
    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(common.Language)
    implicit = Column(Boolean)
    root = Column(Boolean)
    #
    # FIXME: add roots, integrate doublets and disjuncts!
    #
    doublet_comment = Column(Unicode)
    disjunct_comment = Column(Unicode)
    """
    A distinction is further drawn between 
    doublets 
    (variants that are independently supported by the comparative evidence), and 
    disjuncts 
    (variants that are supported only by allowing the overlap of cognate sets).
    To illustrate, both Tagalog gumí ‘beard’ and Malay kumis ‘moustache’ show regular 
    correspondences with Fijian kumi ‘the chin or beard’, but they do not show regular 
    correspondences with one another.  Based on this evidence it is impossible to posit doublets, 
    since independent unambiguous evidence supporting both variants is lacking.  However, since 
    both the Tagalog and Malay forms can be compared with Fijian it is possible to assemble two 
    comparisons that overlap through inclusion of the Fijian form in each. The result is a pair of 
    PMP disjuncts *gumi (based on Tagalog and Fijian) and *kumis (based on Malay and Fijian), 
    either or both of which could be converted to an independent reconstruction if additional 
    comparative support is found.
    """

    etymon_pk = Column(Integer, ForeignKey('reconstruction.pk'))
    sets = relationship(
        'Reconstruction',
        order_by='Reconstruction.subset,Reconstruction.pk',
        foreign_keys=[etymon_pk],
        backref=backref('etymon', remote_side=[pk]))

    explicit_pk = Column(Integer, ForeignKey('reconstruction.pk'))
    implicit_sets = relationship(
        'Reconstruction',
        foreign_keys=[explicit_pk],
        backref=backref('explicit', remote_side=[pk]))

    def grouped_sets(self):
        for ssid, sets in itertools.groupby(self.sets, lambda s: s.subset):
            if ssid:
                yield list(sets)

    def grouped_cognates(self):
        yield from group_counterparts(self.cognates)
