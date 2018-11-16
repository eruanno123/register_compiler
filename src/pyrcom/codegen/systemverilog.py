

from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import namedtuple
from systemrdl.messages import MessagePrinter

import os

# Code generation template root directory
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/template/'

PortDefinition = namedtuple('PortDefinition', 'direction width name')

GeneratorOutput = namedtuple('GeneratorOutput', 'name content')


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


class SystemVerilogGenerator (GeneratorBase):

    def renderCodePart(self, code_part_name, templ_dict):
        """ Renders portion of code identified by argument `code_part_name`.
            Applies the parameters in `templ_dict` on the template.
        """
        self.print_message("info", str.format(
            "Rendering module '{0}'", code_part_name))
        templ = self.env.get_template('sv/reg_' + code_part_name + '.sv')
        return templ.render(templ_dict)

    def renderListedCodeParts(self, code_parts, templ_dict):
        """ Aggregated code rendering """
        render_result = dict()
        for part in code_parts:
            render_result[part] = self.renderCodePart(part, templ_dict)
        return render_result

    def generate(self, rdl_root):

        templ_dict = self.createCommonTemplateDict()

        # TODO: configurable interface
        interface_name = 'interface_apb'
        code_parts_list = ['top', 'backend', interface_name, 'intr', 'field']
        code_parts = self.renderListedCodeParts(code_parts_list, templ_dict)

        combine_template = self.env.get_template('sv/combine.sv')
        combine_dict = {
            'combine_top_module': code_parts['top'],
            'combine_backend_module': code_parts['backend'],
            'combine_interface_module': code_parts[interface_name],
            'combine_field_module': code_parts['field'],
            'combine_intr_module': code_parts['intr']
        }
        combine_code = combine_template.render(combine_dict)

        generic_layout_template = self.env.get_template('sv/generic_layout.sv')
        generic_layout_dict = {
            'file_license_header': '/* All rights reserved */',
            'file_content': combine_code
        }
        result_code = generic_layout_template.render(generic_layout_dict)

        return result_code

        # template_dict = {
        #     'module_name': "SFR_backend",
        #     'hw_ports': [
        #         PortDefinition('output', None, 'test'),
        #         PortDefinition('input', '[10:0]', 'myvector')
        #     ]
        # }
