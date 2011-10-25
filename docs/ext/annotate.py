# coding=utf-8

import re

from docutils import nodes
from pygments.filter import simplefilter
from pygments.token import Comment, Token


# Create the annotation token.
Annotation = Comment.Annotation

# Regular expression pattern for annotations.
annotation_pat = re.compile('(\\(\\w+\\))')


@simplefilter
def annotation_filter(self, lexer, stream, options):
    """Pygments filter for annotations in comments."""
    for ttype, value in stream:
        if ttype is Comment:
            tokens = annotation_pat.split(value)
            # Normal comments are even and labels are odd. Labels include
            # parenthesis at start/end and are stripped by slicing with [1:-1].

            # Special case for a single label in the comment: Drop the leading
            # hash (#).
            if len(tokens) == 3:
                # Strip '#' from the first token.
                if not tokens[0][1:].strip() and not tokens[-1].strip():
                    yield Annotation, tokens[1][1:-1]
                    continue

            for idx, token in enumerate(tokens):
                yield ((ttype, token) if idx % 2 == 0 else
                        (Annotation, token[1:-1]))
            continue
        yield ttype, value


class annotation(nodes.reference):
    pass


def annotation_role(name, rawtext, text, lineno, inliner, options={},
        content=[]):
    return [annotation(rawtext, text)], []


def visit_annotation_html(self, node):
    # Use pygments generated css classes to highlight annotations in HTML
    # ouput.
    self.body.append('<span class="highlight c-Annotation">')


def depart_annotation_html(self, node):
    self.body.append('</span>')


def setup(app):
    # FIXME Hack: Add our own custom filter for highlighting annotations.
    from sphinx.highlighting import PygmentsBridge, lexers
    lexers['python'].add_filter(annotation_filter())

    # Add node and role for annotations.
    app.add_node(annotation, html=(visit_annotation_html,
        depart_annotation_html))
    app.add_role('an', annotation_role)

    # Add custom stylesheet for highlighting annotations.
    app.add_stylesheet('annotation.css')
