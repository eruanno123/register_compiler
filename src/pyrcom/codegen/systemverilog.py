

from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import namedtuple

from systemrdl import RDLWalker, RDLListener
from systemrdl.messages import MessagePrinter
from systemrdl.node import *
from pyrcom.codegen.base import GeneratorBase, GeneratorError

import os

Node
PortDefinition = namedtuple('PortDefinition', 'direction width name')

GeneratorOutput = namedtuple('GeneratorOutput', 'name content')


class SVGeneratorError (GeneratorError):
    """ Represents SystemVerilog generation error """
    pass


class RangeSpecifier:
    """ Represents SV-style ranges like 31:0 """

    def __init__(self, start_idx=0, end_idx=0):
        self.start_idx = start_idx
        self.end_idx = end_idx

    def __str__(self):
        return str(self.start_idx) if (self.start_idx == self.end_idx) \
            else str.format("{0}:{1}", self.start_idx, self.end_idx)


class SignalDeclaration:
    """ General representation of wire/logic declaration """

    def __init__(self, name, kind, range=None):
        self.name = name
        self.kind = kind
        self.range = range

        expectedKind = ["reg", "logic", "wire"]
        if kind not in expectedKind:
            raise SVGeneratorError(str.format(
                "Unknown declaration type '{0}'. Expected values: '{1}'", kind, expectedKind))

    def __str__(self):
        s = str(self.kind)
        if self.range:
            s += ' [' + str(self.range) + ']'
        s += ' ' + self.name + ';'
        return s


class SVSignalDeclarator (GeneratorBase):
    def __init__(self, printer=MessagePrinter(), data_width=32):
        super(SVSignalDeclarator, self).__init__(printer)
        self.data_width = data_width

    def declareRegisterSignals(self, reg_list):
        decl_list = []
        data_range = RangeSpecifier(self.data_width-1, 0)
        for reg in reg_list:
            self.print_message("debug", str.format(
                "declare signals for register '{0}'", reg))
            reg_root_name = 'reg_' + reg + '__'
            decl_list.append(SignalDeclaration(
                reg_root_name + 'select', "logic"))
            decl_list.append(SignalDeclaration(
                reg_root_name + 'data_in', "wire", data_range))
            decl_list.append(SignalDeclaration(
                reg_root_name + 'data_out', "wire", data_range))
        return decl_list

    def declareInterruptSignals(self, intr_list):
        decl_list = []
        for intr in intr_list:
            self.print_message("debug", str.format(
                "declare signals for interrupt '{0}'", intr))
            intr_root_name = 'intr_' + intr + '_'
            for sig in ['enable', 'set', 'clear', 'status']:
                decl_list.append(SignalDeclaration(
                    intr_root_name + sig, "wire"))
        return decl_list


class FlattenListener (RDLListener):
    def __init__(self):
        self._all_regs = []
        self._all_fields = []
        self._all_intr_fields = []

    def enter_Reg(self, node):
        self._all_regs.append(node)

    def enter_Field(self, node):
        self._all_fields.append(node)
        if node.get_property("intr"):
            self._all_intr_fields.append(node)

    @property
    def all_registers(self):
        return self._all_regs

    @property
    def all_fields(self):
        return self._all_fields

    @property
    def all_interrupt_fields(self):
        return self._all_intr_fields


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

    def getInterfacePorts(self, interface_name, templ_dict):
        return self.renderCodePart('interface_' + interface_name + '_ports', templ_dict)

    def getInterfaceCode(self, interface_name, templ_dict):
        return self.renderCodePart('interface_' + interface_name, templ_dict)

    def updateBackendVariables(self, rdl_root: RootNode, templ_dict: dict):

        flat = FlattenListener()
        RDLWalker(unroll=True).walk(rdl_root, flat)

        sigDecl = SVSignalDeclarator(self.printer, 32)
        decl = []
        decl.extend(sigDecl.declareRegisterSignals(
            [r.inst.inst_name for r in flat.all_registers]
        ))
        decl.extend(sigDecl.declareInterruptSignals(
            [r.inst.inst_name for r in flat.all_interrupt_fields]
        ))

        backend_signal_definitions = '\n'.join(str(d) for d in decl)
        templ_dict['backend_signal_definitions'] = backend_signal_definitions

    def generate(self, rdl_root):

        templ_dict = self.createCommonTemplateDict()

        # generate interface code
        # TODO: configurable interface name
        interface_name = 'apb'
        interface_ports = self.getInterfacePorts(interface_name, templ_dict)
        interface_code = self.getInterfaceCode(interface_name, templ_dict)
        templ_dict['interface_name'] = interface_name
        templ_dict['interface_ports'] = interface_ports
        templ_dict['interface_code'] = interface_code

        self.updateBackendVariables(rdl_root, templ_dict)

        # generate common code parts
        code_parts_list = ['top', 'interface', 'backend', 'intr', 'field']
        code_parts = self.renderListedCodeParts(code_parts_list, templ_dict)

        combine_template = self.env.get_template('sv/combine.sv')
        combine_dict = {
            'combine_top_module': code_parts['top'],
            'combine_backend_module': code_parts['backend'],
            'combine_interface_module': code_parts['interface'],
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
