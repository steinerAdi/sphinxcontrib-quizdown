"""
    sphinxcontrib.quizdown
    ~~~~~~~~~~~~~~~~~~~~~~

    Markdownish syntax for generating interactive quizzes

    :copyright: Copyright 2021 by Malte Bonart <malte@spiced-academy.com>
    :license: MIT, see LICENSE for details.
"""

import json
import html
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from docutils import nodes


class Quizdown(SphinxDirective):
    """Implements the quizdown directive
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):

        if self.arguments:
            # external file
            rel_filename, filename = self.env.relfn2path(
                self.arguments[0].strip())
            self.env.note_dependency(rel_filename)
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    quizdown_text = file.read()
            except (IOError, OSError):
                return [self.state.document.reporter.warning(
                    'External quizdown file %r not found or reading '
                    'it failed' % filename, line=self.lineno)]
        else:
            # inline block
            quizdown_text = '\n'.join(self.content)
            if not quizdown_text.strip():
                return [self.state_machine.reporter.warning(
                    'Ignoring "quizdown" directive without content.',
                    line=self.lineno)]
        tag_template = """<div class="quizdown">{code}</div>"""
        html_raw = tag_template.format(code=html.escape(quizdown_text))

        quiznode = nodes.raw(html_raw, html_raw, format='html')

        return [quiznode]


def add_quizdown_lib(app: Sphinx, pagename, templatename, context, doctree):
    quizdown_js = app.config.quizdown_config.setdefault(
        'quizdown_js', 
        'https://cdn.jsdelivr.net/gh/bonartm/quizdown-js@latest/public/build/quizdown.js'
    )

    app.add_js_file(quizdown_js)
    config_json = json.dumps(app.config.quizdown_config)
    app.add_js_file(None, body=f"quizdown.init({config_json});")


def setup(app: Sphinx):
    app.add_directive('quizdown', cls=Quizdown)    
    app.add_config_value('quizdown_config', {}, 'html')
    app.connect('html-page-context', add_quizdown_lib)
    return {
        'version': '0.3',
        'parallel_read_safe': True,
        'parallel_write_safe': True
    }
