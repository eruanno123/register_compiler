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

from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import namedtuple

from systemrdl import RDLWalker, RDLListener
from systemrdl.messages import MessagePrinter
from systemrdl.node import *

from pyrcom.act.common import *
from pyrcom.act.systemverilog import *
from pyrcom.codegen.base import LanguageBuilderBase, LanguageEmitterBase

import os

# =============================================================================

# Add extra properties to FieldNode class
# as described here:
# https://systemrdl-compiler.readthedocs.io/en/release-1.3/properties.html#derived-properties

def test_is_hw_readable (node):
    hw = node.get_property('hw')
    return hw in (rdltypes.AccessType.rw, rdltypes.AccessType.rw1,
                        rdltypes.AccessType.w, rdltypes.AccessType.w1)
FieldNode.add_derived_property(test_is_hw_readable,  'is_hw_readable')

def test_is_hw_writeable (node):
    hw = node.get_property('hw')
    return hw in (rdltypes.AccessType.rw, rdltypes.AccessType.rw1,
                        rdltypes.AccessType.r)
FieldNode.add_derived_property(test_is_hw_writeable, 'is_hw_writeable')

# =============================================================================


class SynthesisContext:
    def __init__(self):
        self._all_regs = []
        self._all_fields = []
        self._all_intr_fields = []

    @property
    def all_registers(self):
        return self._all_regs

    @property
    def all_fields(self):
        return self._all_fields

    @property
    def all_interrupt_fields(self):
        return self._all_intr_fields

# =============================================================================


class SynthesisRDLContext (SynthesisContext, RDLListener):

    def enter_Reg(self, node):
        self._all_regs.append(node)

    def enter_Field(self, node):
        self._all_fields.append(node)
        if node.get_property("intr"):
            self._all_intr_fields.append(node)

# =============================================================================


class Synthesis:
    def __init__(self, context):
        self.context = context  # type: SynthesisContext

    def do_synthesis(self):
        pass

# =============================================================================


class HwPortsSynthesis (Synthesis):

    def get_port_name(self, field):
        return str.format('hw_{0}__{1}',
                    field.parent.inst.inst_name,
                    field.inst.inst_name)

    def do_synthesis(self):
        ports = []
        for field in self.context.all_fields:  # type: FieldNode
            if field.is_hw_writeable:
                bit_high = field.inst.high
                bit_low = field.inst.low
                port_range = Range(field.inst.high, field.inst.low).shift_to_zero() \
                             if (bit_high != bit_low) else None

                port_def = Port(self.get_port_name(field), "output", port_range)
                ports.append(port_def)
        return ports


# =============================================================================

class SynthesisFactory:

    _tools = {
        (Port, "hw_ports"): HwPortsSynthesis
    }

    def __init__(self, context):
        self.context = context

    def create(self, node_type, task) -> Synthesis:
        key = (node_type, str(task))
        tool_type = SynthesisFactory._tools.get(key, None)
        if tool_type:
            return tool_type(self.context)
        else:
            raise CodegenError(
                "Unknown synthesis rule for node type '%s' and task '%s'" % (node_type, task))

# =============================================================================


class SystemVerilogBuilder (LanguageBuilderBase):

    def check(self):
        if 'design_name' not in self.language_config:
            raise CodegenError(
                "Language config does not have required 'design_name' parameter.")

    def build_act(self, rdl_root):
        self.check()

        # Create synthesis context from RDL root node
        synth_context = SynthesisRDLContext()
        RDLWalker(unroll=True).walk(rdl_root, synth_context)

        # Create synthesis tool factory
        synth_toolbox = SynthesisFactory(synth_context)

        # TODO: configurable interface
        interface_name = 'APB'

        top_module_name = self.language_config['design_name']

        #
        # Generate TOP Module
        #
        top_module = TopModule(top_module_name,
                               interface_name=interface_name)

        #
        # Generate Backend Module
        #
        hw_ports_gen = synth_toolbox.create(Port, "hw_ports")
        backend_module = BackendModule(top_module_name + '_backend',
                                       hw_ports=hw_ports_gen.do_synthesis())

        interface_module = InterfaceModule(
            top_module_name + '_interface', interface_name=interface_name)

        field_module = FieldModule(top_module_name + '_field')
        intr_module = InterruptModule(top_module_name + '_intr')

        root = GenericLayout(self.language_config.get('file_header', ''),
                             self.language_config.get('file_footer', ''),
                             Composite(top_module, backend_module, interface_module, field_module, intr_module))

        return root


class SystemVerilogEmitter (LanguageEmitterBase):

    def visit_GenericLayout(self, node):
        return self.render('GenericLayout', **{
            'file_header': node.header,
            'file_footer': node.footer,
            'file_content': [self.visit(c) for c in node.children]
        })

    def visit_Composite(self, node):
        return self.render('Composite', children=[self.visit(c) for c in node.children])

    def visit_TopModule(self, node):
        interface_template = 'interfaces/' + node.interface_name
        interface_ports = self.render(interface_template + '_port')
        return self.render('modules/TopModule',
                           module_name=node.module_name,
                           interface_ports=interface_ports)

    def visit_BackendModule(self, node):
        hw_ports_list = [self.visit(p) for p in node.hw_ports]
        return self.render('modules/BackendModule',
                           module_name=node.module_name,
                           hw_ports=hw_ports_list)

    def visit_InterfaceModule(self, node):
        interface_template = 'interfaces/' + node.interface_name
        interface_code = self.render(interface_template)
        interface_ports = self.render(interface_template + '_port')
        return self.render('modules/InterfaceModule',
                           module_name=node.module_name,
                           interface_name=node.interface_name,
                           interface_ports=interface_ports,
                           interface_code=interface_code)

    def visit_FieldModule(self, node):
        return self.render('modules/FieldModule', module_name=node.module_name)

    def visit_InterruptModule(self, node):
        return self.render('modules/InterruptModule', module_name=node.module_name)

    def visit_Port(self, node):
        return self.render('Port', port=node)

