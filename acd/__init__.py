import collections

from pyramid.config import Configurator

from clld_glottologfamily_plugin import util

from clld.interfaces import IMapMarker, IValueSet, IValue, IDomainElement
from clldutils.svg import pie, icon, data_url

# we must make sure custom models are known at database initialization!
from acd import models
from acd import datatables



class LanguageByFamilyMapMarker(util.LanguageByFamilyMapMarker):
    def __call__(self, ctx, req):
    
        if IValueSet.providedBy(ctx):
            if ctx.language.family:
                return data_url(icon(ctx.language.family.jsondata['icon']))
            return data_url(icon(req.registry.settings.get('clld.isolates_icon', util.ISOLATES_ICON)))
    
        return super(LanguageByFamilyMapMarker, self).__call__(ctx, req)



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')

    config.include('clld_cognacy_plugin')
    config.include('clldmpg')
    #config.register_map('cognateset', maps.CognateSetMap)
    config.register_datatable('cognatesets', datatables.Etyma)

    config.registry.registerUtility(LanguageByFamilyMapMarker(), IMapMarker)

    return config.make_wsgi_app()
