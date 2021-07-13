import re
import textwrap

from markdown import markdown as base_markdown


def markdown(req, s):
    s = base_markdown(s)
    s = re.sub(
        'languages/(?P<lid>[0-9]+)', lambda m: req.route_url('language', id=m.group('lid')), s)
    return s


def shorten(text):
    return textwrap.shorten(text, width=30, placeholder='\u2026')
