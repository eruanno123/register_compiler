
from systemrdl.messages import MessagePrinter
from jinja2 import Environment, FileSystemLoader

import os

# Code generation template root directory
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/template/'


class GeneratorError (Exception):
    """ Base class representing generator exception """
    pass


class GeneratorBase:
    def __init__(self, printer=MessagePrinter(), **kwargs):
        self.config = kwargs
        self.root_name = kwargs.pop('root_name', 'reg')

        self.printer = printer
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR)
        )

    def print_message(self, severity, text, src_ref=None):
        """ Wrapper to printer.print_message allowing default `src_ref` """
        self.printer.print_message(severity, text, src_ref)

    def createCommonTemplateDict(self):
        return {
            'module_root_name': self.root_name
        }
