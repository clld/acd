import collections

from pyramid.config import Configurator

from clld.web.icon import MapMarker
from clld.interfaces import IMapMarker, IValueSet, IValue, IDomainElement, ILanguage, ILinkAttrs
from clldutils.svg import pie, icon, data_url
from clldutils import color

# we must make sure custom models are known at database initialization!
from acd import models
from acd import datatables

ICONS = collections.OrderedDict([
    ('Form.', ''),
    ('WMP', ''),
    ('CMP', ''),
    ('SHWNG', ''),
    ('OC', ''),
])
for k, c in zip(ICONS.keys(), color.sequential_colors(len(ICONS))):
    ICONS[k] = c.replace('#', 'c')


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
    config.register_datatable('cognatesets', datatables.Etyma)

    config.registry.registerUtility(LanguageByGroupMapMarker(), IMapMarker)

    return config.make_wsgi_app()
