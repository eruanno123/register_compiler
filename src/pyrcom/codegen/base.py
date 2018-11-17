# Copyright © 2018 Mateusz Maciąg
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from systemrdl.messages import MessagePrinter
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateError

from pyrcom.exceptions import CodegenTemplateError
from pyrcom.act.common import ACTBuilder, ACTVisitor, ACTNode

import os


# =============================================================================

class LanguageComponent:
    def __init__(self, language_config=dict(), printer=MessagePrinter()):
        self._config = language_config
        self._printer = printer

    @property
    def language_config(self) -> dict:
        return self._config

    @property
    def printer(self):
        return self._printer

# =============================================================================


class LanguageBuilderBase (LanguageComponent, ACTBuilder):
    def __init__(self, language_config=dict(), printer=MessagePrinter()):
        LanguageComponent.__init__(self, language_config, printer)
        ACTBuilder.__init__(self)

# =============================================================================


class LanguageEmitterBase (LanguageComponent, ACTVisitor):

    DEFAULT_TEMPLATE_DIR = os.path.dirname(
        os.path.abspath(__file__)) + '/template/'
    DEFAULT_TEMPLATE_SUFFIX = ''

    def __init__(self,
                 language_name,
                 language_config=dict(),
                 env=Environment(loader=FileSystemLoader(
                     DEFAULT_TEMPLATE_DIR)),
                 printer=MessagePrinter(),
                 template_suffix=DEFAULT_TEMPLATE_SUFFIX):
        LanguageComponent.__init__(self, language_config, printer)
        ACTVisitor.__init__(self)
        self._language_name = language_name
        self._env = env
        self._template_suffix = template_suffix

    def get_template(self, template_name):
        path = self._language_name + '/' + template_name + self._template_suffix
        return self._env.get_template(path)

    def render(self, template_name, **kwargs):
        return self.get_template(template_name).render(kwargs)

    def print_message(self, severity, text, src_ref=None):
        """ Wrapper to printer.print_message allowing default `src_ref` """
        self._printer.print_message(severity, text, src_ref)

    def generate_code(self, language_builder, rdl_root):
        try:
            act_root = language_builder.build_act(rdl_root)
            return self.visit(act_root)
        except TemplateError as e:
            raise CodegenTemplateError() from e
        # raise CodegenTemplateError("Code template error", inner_error=e)

    @property
    def language_name(self):
        return self._language_name
