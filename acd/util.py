import re
import textwrap

from markdown import markdown as base_markdown
from clld.db.meta import DBSession
from clld.web.util import helpers
from clld.web.util.htmllib import HTML

from acd.models import Variety


def markdown(req, s):
    s = base_markdown(s)
    s = re.sub(
        'languages/(?P<lid>[0-9]+)', lambda m: req.route_url('language', id=m.group('lid')), s)
    return s


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