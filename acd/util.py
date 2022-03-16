import math
import textwrap
import collections

from unidecode import unidecode
from markdown import Markdown
from markdown.extensions.toc import TocExtension
from clld.db.meta import DBSession
from clld.db.models import common
from clld.web.util import helpers
from clld.web.util.htmllib import HTML
from cldfviz.text import CLDFMarkdownLink

from acd.models import Variety, Reconstruction, Formset
assert Formset


def cognateset_index_html(request=None, context=None, **kw):
    initials = collections.Counter()
    for cs in DBSession.query(Reconstruction).filter(Reconstruction.etymon_pk == None):
        initials.update(cs.form_initials)
    initials = [
        (c, v, math.ceil(v / 10))
        for c, v in sorted(initials.items(), key=lambda i: unidecode(i[0]).lower())]
    return dict(initials=initials)


def formset_index_html(request=None, context=None, **kw):
    return {c.id: c for c in DBSession.query(common.Contribution)}


def markdown(req, s):
    def repl(ml):
        comp_to_route = {
            'LanguageTable': 'language',
            'Source': 'source',
        }
        if ml.is_cldf_link:
            try:
                ml.url = req.route_url(comp_to_route[ml.component()], id=ml.objid)
            except:
                print(ml.component(), ml)
        return ml

    md = Markdown(extensions=[
        TocExtension(permalink=True),
        'markdown.extensions.fenced_code',
        'markdown.extensions.tables'])
    return md.convert(CLDFMarkdownLink.replace(s, repl)), md


def shorten(text):
    return textwrap.shorten(text, width=30, placeholder='\u2026')


def proto_tree(req, selected):
    """\
           ┌─Formosan
──PAN──────┤
           │          ┌─PWMP──── ──PPh
           └─PMP──────┤
                      │          ┌─PCMP
                      └─PCEMP────┤
                                 │          ┌─PSHWNG
                                 └─PEMP─────┤
                                            └─POC
    """
    plangs = {l.group: l for l in DBSession.query(Variety).filter(
        Variety.group.in_('PAN PMP PWMP PPh PCEMP PCMP PEMP PSHWNG POC'.split()))}

    def link(req, l):
        return helpers.link(req, l) if l != selected else HTML.strong(l.group)

    return HTML.table(
        HTML.tr(
            HTML.td(' '),
            HTML.td(link(req, plangs['PAN'])),
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(' '),
        ),
        HTML.tr(
            HTML.td(HTML.div(class_='lline')),
            HTML.td(HTML.div(class_='rline')),
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(' '),
        ),
        HTML.tr(
            HTML.td('Form.'),
            HTML.td(' '),
            HTML.td(link(req, plangs['PMP'])),
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(' '),
        ),
        HTML.tr(
            HTML.td(' '),
            HTML.td(HTML.div(class_='lline')),
            HTML.td(HTML.div(class_='rline')),
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(' '),
        ),
        HTML.tr(
            HTML.td(' '),
            HTML.td(link(req, plangs['PWMP'])),
            HTML.td(' '),
            HTML.td(link(req, plangs['PCEMP'])),
            HTML.td(' '),
            HTML.td(' '),
        ),
        HTML.tr(
            HTML.td(HTML.div(class_='lline')),
            HTML.td(' '),
            HTML.td(HTML.div(class_='lline')),
            HTML.td(HTML.div(class_='rline')),
            HTML.td(' '),
            HTML.td(' '),
        ),
        HTML.tr(
            HTML.td(link(req, plangs['PPh'])),
            HTML.td(' '),
            HTML.td(link(req, plangs['PCMP'])),
            HTML.td(' '),
            HTML.td(link(req, plangs['PEMP'])),
            HTML.td(' '),
        ),
        HTML.tr(
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(HTML.div(class_='lline')),
            HTML.td(HTML.div(class_='rline')),
            HTML.td(' '),
        ),
        HTML.tr(
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(' '),
            HTML.td(link(req, plangs['PSHWNG'])),
            HTML.td(' '),
            HTML.td(link(req, plangs['POC'])),
        ),
        class_='noborder',
    )
