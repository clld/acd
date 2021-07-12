import textwrap

from markdown import markdown


def shorten(text):
    return textwrap.shorten(text, width=30, placeholder='\u2026')
