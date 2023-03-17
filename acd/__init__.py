import functools
import collections

from pyramid.config import Configurator
from sqlalchemy.orm import joinedload

from clld.web.icon import MapMarker
from clld.web.app import menu_item
from clld.interfaces import IMapMarker, IValueSet, IValue, ILanguage, ILinkAttrs, IIndex, ICtxFactoryQuery
from clld.web.app import CtxFactoryQuery
from clld.db.models.common import Value, ValueSet, Contribution
from clldutils.svg import pie, icon, data_url
from clldutils import color
from clld_cognacy_plugin.interfaces import ICognateset
from clld_cognacy_plugin.models import Cognateset, Cognate

# we must make sure custom models are known at database initialization!
from acd import models
from acd import datatables
from acd import maps
from acd import adapters
from acd.interfaces import IFormset

ICONS = collections.OrderedDict([
    ('Form.', ''),
    ('WMP', ''),
    ('CMP', ''),
    ('SHWNG', ''),
    ('OC', ''),
])
for k, c in zip(ICONS.keys(), color.sequential_colors(len(ICONS))):
    ICONS[k] = c.replace('#', 'c')


class CtxFactory(CtxFactoryQuery):
    def refined_query(self, query, model, req):
        if model == Cognateset:
            query = query.options(
                joinedload(models.Reconstruction.sets).joinedload(models.Reconstruction.language),
                joinedload(models.Reconstruction.sets).joinedload(Cognateset.cognates).joinedload(Cognate.counterpart).joinedload(Value.valueset).joinedload(ValueSet.language),
                joinedload(models.Reconstruction.sets).joinedload(Cognateset.cognates).joinedload(Cognate.counterpart).joinedload(Value.valueset).joinedload(ValueSet.parameter),
            )
        if model == Contribution:
            query = query.options()
        return query


def link_attrs(req, obj, **kw):
    if ILanguage.providedBy(obj):
        if obj.is_proto:
            kw['class'] = 'proto-language'
            kw['label'] = obj.group if obj.group.startswith('P') else obj.name
        else:
            kw['class'] = 'language'

    if IValueSet.providedBy(obj):
        if obj.language.is_proto:
            kw['class'] = 'proto-form'
            v = obj.values[0]
            if v.reconstruction:
                if v.reconstruction.implicit:
                    kw['class'] += ' implicit'
                kw['href'] = req.route_url('cognateset', id=v.reconstruction.etymon.id, _anchor='s-{}'.format(v.reconstruction.id.split('-')[0]))
                kw['title'] = 'Go to etymon page'
        else:
            kw['class'] = 'form'

    if IValue.providedBy(obj):
        if obj.valueset.language.is_proto:
            kw['class'] = 'proto-form'
            if obj.reconstruction:
                kw['href'] = req.route_url('cognateset', id=obj.reconstruction.etymon.id, _anchor='s-{}'.format(obj.reconstruction.id.split('-')[0]))
        else:
            kw['class'] = 'form'

    return kw


class LanguageByGroupMapMarker(MapMarker):
    def __call__(self, ctx, req):
        group = None
        if ILanguage.providedBy(ctx):
            if ctx.group in ICONS:
                group = ctx.group

        if IValueSet.providedBy(ctx):
            if ctx.language.group in ICONS:
                group = ctx.language.group

        if group:
            return data_url(icon(ICONS[group]))
        return super(LanguageByGroupMapMarker, self).__call__(ctx, req)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.registry.registerUtility(link_attrs, ILinkAttrs)
    config.include('clld_cognacy_plugin')
    config.include('clldmpg')
    #config.register_map('cognateset', maps.CognateSetMap)

    config.register_menu(
        ('dataset', functools.partial(menu_item, 'dataset', label='Home')),
        ('cognatesets', functools.partial(menu_item, 'cognatesets', label='Cognatesets')),
        #Roots Loans Near Noise
        ('roots', lambda ctx, req: (req.route_url('contribution', id='Root'), 'Roots')),
        ('loans', lambda ctx, req: (req.route_url('contribution', id='Loan'), 'Loans')),
        ('near', lambda ctx, req: (req.route_url('contribution', id='Near'), 'Near Cognates')),
        ('noise', lambda ctx, req: (req.route_url('contribution', id='Noise'), 'Chance Resemblances')),
        ('languages', functools.partial(menu_item, 'languages', label='Languages')),
        ('sources', functools.partial(menu_item, 'sources', label='Sources')),
    )

    config.register_datatable('cognatesets', datatables.Etyma)
    config.register_resource('formset', models.Formset, IFormset, with_index=True)
    config.register_map('cognateset', maps.ReconstructionMap)
    config.register_adapter(
        adapters.GeoJsonReconstruction,
        ICognateset,
        name=adapters.GeoJsonReconstruction.mimetype)
    config.registry.registerUtility(LanguageByGroupMapMarker(), IMapMarker)
    config.registry.registerUtility(CtxFactory(), ICtxFactoryQuery)

    return config.make_wsgi_app()
