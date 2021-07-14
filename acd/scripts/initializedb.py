import collections

from pycldf import Sources
from clldutils.misc import nfilter
from clldutils.misc import slug
from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib import bibtex
from nameparser import HumanName

from clld_cognacy_plugin.models import Cognate

import acd
from acd import models


def main(args):
    data = Data()
    ds = data.add(
        common.Dataset,
        acd.__name__,
        id=acd.__name__,
        domain='acd.clld.org',
        name="ACD - Austronesian Comparative Dictionary",
        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'},
    )
    contrib = data.add(
        common.Contribution,
        None,
        id='cldf',
        name=args.cldf.properties.get('dc:title'),
        description=args.cldf.properties.get('dc:bibliographicCitation'),
    )
    for i, name in enumerate(['Robert Blust', 'Stephen Trussel']):
        common.Editor(
            dataset=ds,
            ord=i,
            contributor=common.Contributor(id=slug(HumanName(name).last), name=name)
        )

    #
    # include (the 9) proto-languages and language groups
    #
    for lang in args.cldf.iter_rows('LanguageTable', 'id', 'glottocode', 'name', 'latitude', 'longitude'):
        data.add(
            models.Variety,
            lang['id'],
            id=lang['id'],
            name=lang['name'],
            latitude=lang['latitude'],
            longitude=lang['longitude'],
            glottocode=lang['glottocode'],
            group=lang['Group'],
            is_proto=lang['name'].startswith('Proto'),
        )

    for rec in bibtex.Database.from_file(args.cldf.bibpath, lowercase=True):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

    refs = collections.defaultdict(list)


    for param in args.cldf.iter_rows('ParameterTable', 'id', 'concepticonReference', 'name'):
        data.add(
            models.Concept,
            param['id'],
            id=param['id'],
            name='{} [{}]'.format(param['name'], param['id']),
        )
    for form in args.cldf.iter_rows('FormTable', 'id', 'form', 'languageReference', 'parameterReference', 'source'):
        vsid = (form['languageReference'], form['parameterReference'])
        vs = data['ValueSet'].get(vsid)
        if not vs:
            vs = data.add(
                common.ValueSet,
                vsid,
                id='-'.join(vsid),
                language=data['Variety'][form['languageReference']],
                parameter=data['Concept'][form['parameterReference']],
                contribution=contrib,
            )
        for ref in form.get('source', []):
            sid, pages = Sources.parse(ref)
            refs[(vsid, sid)].append(pages)
        data.add(
            common.Value,
            form['id'],
            id=form['id'],
            name=form['form'],
            valueset=vs,
        )

    for cs in args.cldf.iter_rows('CognatesetTable', 'id'):
        data.add(
            acd.models.Reconstruction,
            cs['id'],
            id=cs['id'],
            name=cs['Form'],
            description=cs['Description'],
            proto_language=cs['Proto_Language'],
            comment=cs['Comment'],
        )

    for cs in args.cldf['protoforms.csv']:
        form = data['Value'][cs['Form_ID']]
        data.add(
            acd.models.Reconstruction,
            cs['ID'],
            id=cs['ID'],
            name=form.name,
            description=form.valueset.parameter.name.split('[')[0].strip(),
            etymon=data['Reconstruction'][cs['Cognateset_ID']],
            proto_language=cs['Proto_Language'],
            language=form.valueset.language,
            form=form,
            comment=cs['Comment'],
            subset=int(cs['Subset']) if cs['Subset'] is not None else None,
            implicit=cs['Inferred'],
        )

    DBSession.flush()
    for cs in args.cldf['protoforms.csv']:
        if cs['Inferred']:
            data['Reconstruction'][cs['ID']].explicit_pk = data['Reconstruction'][cs['ID'].split('-')[0]].pk

    for cog in args.cldf.iter_rows('CognateTable', 'id', 'formReference', 'cognatesetReference'):
        data.add(
            Cognate,
            cog['id'],
            cognateset=data['Reconstruction'][cog['cognatesetReference']],
            counterpart=data['Value'][cog['formReference']],
        )
        data.add(
            Cognate,
            cog['id'],
            cognateset=data['Reconstruction'][cog['Reconstruction_ID']],
            counterpart=data['Value'][cog['formReference']],
        )

    for (vsid, sid), pages in refs.items():
        DBSession.add(common.ValueSetReference(
            valueset=data['ValueSet'][vsid],
            source=data['Source'][sid],
            description='; '.join(nfilter(pages))
        ))


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
