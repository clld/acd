import collections
import unicodedata

from unidecode import unidecode
from pycldf import Sources
from clldutils.misc import nfilter
from clldutils.misc import slug
from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clld.db import fts
from clld.db.models import common
from clld.lib import bibtex
from nameparser import HumanName

from clld_cognacy_plugin.models import Cognate

import acd
from acd import models


def initials(s):
    for i, c in enumerate(unidecode(s)):
        if unicodedata.category(c).startswith('L'):
            return 'l' if c == 'L' else c
        if c == '(':
            alternatives = s[i + 1:].split(')')[0]
            if ',' in alternatives:
                return ''.join(set(initials(ss) for ss in alternatives.split(',')))
            return alternatives


def main(args):
    fts.index('fts_index', models.Reconstruction.gloss, DBSession.bind)
    data = Data()
    ds = data.add(
        common.Dataset,
        acd.__name__,
        id=acd.__name__,
        domain='acd.clld.org',
        name="ACD - Austronesian Comparative Dictionary",
        description=args.cldf.directory.parent.joinpath('NOTES.md').read_text(encoding='utf8'),
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

    for c in args.cldf.iter_rows('ContributionTable', 'id', 'name', 'description'):
        data.add(
            common.Contribution,
            c['id'],
            id=c['id'],
            name=c['name'],
            description=c['description'],
        )

    for rec in bibtex.Database.from_file(args.cldf.bibpath, lowercase=True):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

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
            parent_language=lang['Dialect_Of'],
        )
    DBSession.flush()
    for lang in args.cldf.iter_rows('LanguageTable', 'id', 'source'):
        for sid in lang['source']:
            DBSession.add(common.LanguageSource(
                language_pk=data['Variety'][lang['id']].pk,
                source_pk=data['Source'][sid].pk))

    refs = collections.defaultdict(list)

    #
    # Add the form-meaning pairs:
    #
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
            models.Form,
            form['id'],
            id=form['id'],
            name=form['form'],
            valueset=vs,
        )

    #
    # Add the Etyma:
    #
    for cs in args.cldf.iter_rows('CognatesetTable', 'id'):
        if cs['Contribution_ID'] in ['Canonical']:
            data.add(
                acd.models.Reconstruction,
                cs['id'],
                id=cs['id'],
                name=cs['Form'],
                form_initials=initials(cs['Form']),
                description=cs['Description'],
                gloss=fts.tsvector(cs['Description']),
                proto_language=cs['Proto_Language'],
                comment=cs['Comment'],
                root=cs['Contribution_ID'] == 'Root',
            )
        else:
            data.add(
                acd.models.Formset,
                cs['id'],
                id=cs['id'],
                name=cs['Description'] if cs['Contribution_ID'] != 'Root' else cs['Form'],
                description=cs['Description'] if cs['Contribution_ID'] != 'Root' else None,
                comment=cs['Comment'],
                contribution=data['Contribution'][cs['Contribution_ID']],
            )

    #
    # Add the reconstructions
    #
    for cs in args.cldf['protoforms.csv']:
        form = data['Form'][cs['Form_ID']]
        data.add(
            acd.models.Reconstruction,
            cs['ID'],
            id=cs['ID'],
            name=form.name,
            description=form.valueset.parameter.name.split('[')[0].strip(),
            gloss=fts.tsvector(form.valueset.parameter.name.split('[')[0].strip()),
            etymon=data['Reconstruction'][cs['Cognateset_ID']],
            proto_language=cs['Proto_Language'],
            language=form.valueset.language,
            form=form,
            comment=cs['Comment'],
            subset=int(cs['Subset']) if cs['Subset'] is not None else None,
            implicit=cs['Inferred'],
            #
            # FIXME: implement doublets and disjuncts as proper relations!
            # doublets and disjuncts must be in the same proto_language!
            #
            doublet_comment=cs['Doublet_Comment'],
            disjunct_comment=cs['Disjunct_Comment'],
        )

    DBSession.flush()
    for cs in args.cldf['protoforms.csv']:
        for rel in ['doublet', 'disjunct']:
            for rid in cs[rel.capitalize() + 's']:
                DBSession.add(models.ReconstructionRelation(
                    source_pk=data['Reconstruction'][cs['ID']].pk,
                    target_pk=data['Reconstruction'][rid].pk,
                    type=rel
                ))
        if cs['Inferred']:
            data['Reconstruction'][cs['ID']].explicit_pk = data['Reconstruction'][cs['ID'].split('-')[0]].pk

    for cog in args.cldf.iter_rows('CognateTable', 'id', 'formReference', 'cognatesetReference'):
        if cog['cognatesetReference'] in data['Reconstruction']:
            # We add cognates to the etymon as well as to the "nearest" explicit reconstruction
            data.add(
                Cognate,
                cog['id'],
                cognateset=data['Reconstruction'][cog['cognatesetReference']],
                counterpart=data['Form'][cog['formReference']],
            )
            data.add(
                Cognate,
                cog['id'],
                cognateset=data['Reconstruction'][cog['Reconstruction_ID']],
                counterpart=data['Form'][cog['formReference']],
            )
        else:
            assert cog['cognatesetReference'] in data['Formset']
            data.add(
                models.Member,
                cog['id'],
                formset=data['Formset'][cog['cognatesetReference']],
                counterpart=data['Form'][cog['formReference']],
            )

    for cs in args.cldf['loansets.csv']:
        data.add(
            acd.models.Formset,
            cs['ID'],
            id=cs['ID'],
            name=cs['Gloss'],
            comment=cs['Comment'],
            contribution=data['Contribution']['Loan'],
            # FIXME: Dempwolff Etymology!
        )
    for cs in args.cldf['BorrowingTable']:
        data.add(
            models.Member,
            cs['ID'],
            formset=data['Formset'][cs['Loanset_ID']],
            counterpart=data['Form'][cs['Target_Form_ID']],
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
    #
    # determine "Formosan only" reconstructions
    #
