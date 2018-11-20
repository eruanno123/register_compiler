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

def test_is_hw_readable (node: Node):
    hw = node.get_property('hw')
    return hw in (rdltypes.AccessType.rw, rdltypes.AccessType.rw1,
                        rdltypes.AccessType.w, rdltypes.AccessType.w1)
FieldNode.add_derived_property(test_is_hw_readable,  'is_hw_readable')

def test_is_hw_writeable (node: Node):
    hw = node.get_property('hw')
    return hw in (rdltypes.AccessType.rw, rdltypes.AccessType.rw1,
                        rdltypes.AccessType.r)
FieldNode.add_derived_property(test_is_hw_writeable, 'is_hw_writeable')

def test_is_interrupt_flag (node: Node):
    return node.get_property('intr')

FieldNode.add_derived_property(test_is_interrupt_flag, 'is_interrupt_flag')

# =============================================================================
# Custon jinja2 filters

def verilog_literal(value, format='b', width=32):
    if format == 'b':
        return str.format("{}'b{:b}", width, value)
    elif format == 'd':
        return str.format("{}'d{}", width, value)
    elif format == 'x':
        return str.format("{}'h{:x}", width, value)
    else:
        return "<error>"

# =============================================================================


class SynthesisContext:
    def __init__(self):
        self._all_regs = []
        self._all_fields = []
        self._all_intr_fields = []
        self._undriven_nets = []
        self._unused_nets = []

    def add_undriven_net(self, net):
        self._undriven_nets.append(net)

    def add_unused_net(self, net):
        self._unused_nets.append(net)

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
        if node.is_interrupt_flag:
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
                port_range = Range(bit_high, bit_low).shift_to_zero() \
                             if (bit_high != bit_low) else None

                port_def = Port(self.get_port_name(field), "output", port_range)
                ports.append(port_def)
        return ports


# =============================================================================

class HwRegSignalDeclarationSynthesis (Synthesis):

    def do_synthesis(self):
        decl = []
        decl_spec = [
            ("select", "logic", None),
            ("data_in", "wire", Range(31,0)),
            ("data_out", "wire", Range(31,0))
        ]
        for reg in self.context.all_registers: # type: RegNode
            base_name = 'reg_' + reg.inst.inst_name + '__'
            decl.extend(
                [SignalDeclaration(base_name + spec[0], spec[1], spec[2]) for spec in decl_spec]
            )
        return decl

class HwIntrSignalDeclarationSynthesis (Synthesis):

    def do_synthesis(self):
        decl = []
        intr_sig = [ "enable", "set", "clear", "status" ]
        for intr in self.context.all_interrupt_fields: # type: FieldNode
            base_name = 'intr_' + intr.inst.inst_name + '_'
            decl.extend(
                [SignalDeclaration(base_name + sig, "wire") for sig in intr_sig]
            )
        return decl

# =============================================================================

class RegisterInstantiationSynthesis (Synthesis):

    def synthesize_field(self, field: FieldNode):
        parent_reg_name = field.parent.inst.inst_name
        field_name  = field.inst.inst_name
        field_range = Range(field.inst.high, field.inst.low)
        if field.is_interrupt_flag:
            return FieldBypass(parent_reg_name, field_name, field_range)
        else:
            reset_mask = field.get_property("reset_mask", default=0)
            reset_val = field.get_property("reset")
            return FieldInstance(parent_reg_name, field_name, field_range, reset_mask, reset_val)

    def do_synthesis(self):
        reg_inst_list = []
        for reg in self.context.all_registers: # type: RegNode
            reg_name = reg.inst.inst_name
            reg_offset= reg.address_offset

            field_inst_list = []
            for field in reg.fields(): # TODO: use skip_not_present arg
                field_name = field.inst.inst_name
                field_group_desc = str.format("Field: {}", field_name)
                field_data = self.synthesize_field(field)
                field_group = LogicalGroup(2, field_group_desc, field_data)
                field_inst_list.append(field_group)

            reg_group_desc = str.format("Register: {:20} (offset +0x{:08X})", reg_name, reg_offset)
            reg_group = LogicalGroup(2, reg_group_desc, field_inst_list)
            reg_inst_list.append(reg_group)
        return reg_inst_list

class InterruptInstantiationSynthesis (Synthesis):

    def synthesize_intr(self, intr_name):
        return InterruptInstance(intr_name)

    def do_synthesis(self):
        intr_inst_list = []
        for intr in self.context.all_interrupt_fields: # type: FieldNode
            intr_name = intr.inst.inst_name
            intr_group_desc = str.format("Interrupt: {}", intr_name)
            intr_data = self.synthesize_intr(intr_name)
            intr_group = LogicalGroup(2, intr_group_desc, intr_data)
            intr_inst_list.append(intr_group)
        return intr_inst_list
# =============================================================================

class CaseAssignment (Assignment):
    def __init__(self,
                 case_id,
                 lhs, rhs):
        super(CaseAssignment, self).__init__(lhs, rhs)
        self._case_id = case_id

    @property
    def case_id(self):
        return self._case_id

class WriteSelectDecoder (SelectDecoder):
    def __init__(self, address_map):
        super(WriteSelectDecoder, self).__init__(address_map)

class WriteSelectDecoderSynthesis (Synthesis):

    def make_signal_name(self, reg_name):
        return str.format("reg_{}__select", reg_name)

    def do_synthesis(self):
        addr_map = []
        for reg in self.context.all_registers: # type: RegNode
            addr_map.append( (int(reg.address_offset/4), self.make_signal_name(reg.inst.inst_name)) )
        return WriteSelectDecoder(addr_map)

# =============================================================================


class SynthesisFactory:

    _tools = {
        "hw_ports" : HwPortsSynthesis,
        "hw_reg_signals": HwRegSignalDeclarationSynthesis,
        "hw_intr_signals": HwIntrSignalDeclarationSynthesis,
        "hw_reg_instances": RegisterInstantiationSynthesis,
        "hw_intr_instances" : InterruptInstantiationSynthesis,
        "write_sel_decoder" : WriteSelectDecoderSynthesis,
    }

    def __init__(self, context):
        self.context = context

    def create(self, task) -> Synthesis:
        key = str(task)
        tool_type = SynthesisFactory._tools.get(key, None)
        if tool_type:
            return tool_type(self.context)
        else:
            raise CodegenError(
                "Unknown synthesis rule '%s'" % task)

    def synthesise(self, task):
        return self.create(task).do_synthesis()

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
        # Generate Backend Module
        #
        hw_ports = synth_toolbox.synthesise("hw_ports")

        backend_reg_decl = synth_toolbox.synthesise("hw_reg_signals")
        backend_intr_decl = synth_toolbox.synthesise("hw_intr_signals")

        field_instances = synth_toolbox.synthesise("hw_reg_instances")
        intr_instances = synth_toolbox.synthesise("hw_intr_instances")

        write_sel_decoder = synth_toolbox.synthesise("write_sel_decoder")

        backend_module = BackendModule(top_module_name + '_backend',
            hw_ports=hw_ports,
            backend_signal_declarations=LogicalGroup(1, "Auto-Generated Signals", Composite(
                LogicalGroup(2, "Register signals", backend_reg_decl),
                LogicalGroup(2, "Interrupt signals", backend_intr_decl),
            )),
            backend_instantiation=Composite(
                LogicalGroup(1, "REGISTER FILE DEFINITION", field_instances),
                LogicalGroup(1, "INTERRUPT DEFINITION", intr_instances)
            ),
            write_select_decoder=write_sel_decoder
        )

        interface_module = InterfaceModule(
            top_module_name + '_interface', interface_name=interface_name)

        field_module = FieldModule(top_module_name + '_field')
        intr_module = InterruptModule(top_module_name + '_intr')

        #
        # Generate TOP Module
        #
        top_module = TopModule(top_module_name,
                               interface_name=interface_name,
                               hw_ports=hw_ports)

        root = GenericLayout(self.language_config.get('file_header', ''),
                             self.language_config.get('file_footer', ''),
                             Composite(top_module, backend_module, interface_module, field_module, intr_module))

        return root


class SystemVerilogEmitter (LanguageEmitterBase):

    def do_prebuild(self, rdl_root):
        self.print_message("debug", "pre-build event")
        self.add_jinja_filter("verilog_literal", verilog_literal)

    def visit_GenericLayout(self, node: GenericLayout):
        return self.render('GenericLayout', **{
            'file_header': node.header,
            'file_footer': node.footer,
            'file_content': self.default_visit(node)
        })

    def visit_Composite(self, node: Composite):
        return self.render('Composite', children=self.default_visit(node))

    def visit_LogicalGroup(self, node: LogicalGroup):
        return self.render('LogicalGroupH%d' % node.level,
            description=node.description,
            content=self.default_visit(node))

    def visit_FieldBypass(self, node: FieldBypass):
        return self.render('instances/FieldBypass',
            node=node,
            module_name=self.language_config['design_name'])

    def visit_FieldInstance(self, node: FieldInstance):
        return self.render('instances/FieldInstance',
            node=node,
            module_name=self.language_config['design_name'])

    def visit_InterruptInstance(self, node: InterruptInstance):
        return self.render('instances/IntrInstance',
            node=node,
            module_name=self.language_config['design_name'])

    def visit_WriteSelectDecoder(self, node: WriteSelectDecoder):
        return self.render('WriteSelectDecoder', address_map=node.address_map)

    def visit_TopModule(self, node: TopModule):
        interface_template = 'interfaces/' + node.interface_name
        interface_ports = self.render(interface_template + '_port')
        hw_ports_list = self.visit(node.hw_ports)
        return self.render('modules/TopModule',
                           module_name=node.module_name,
                           interface_ports=interface_ports,
                           hw_ports=hw_ports_list)

    def visit_BackendModule(self, node: BackendModule):
        hw_ports_list = self.visit(node.hw_ports)
        backend_signal_decl = self.visit(node.backend_signal_declarations)
        backend_instantiation = self.visit(node.backend_instantiation)
        write_select_decoder = self.visit(node.write_select_decoder)
        return self.render('modules/BackendModule',
                           module_name=node.module_name,
                           hw_ports=hw_ports_list,
                           backend_signal_declarations=backend_signal_decl,
                           backend_instantiation=backend_instantiation,
                           write_select_decoder=write_select_decoder)

    def visit_InterfaceModule(self, node: InterfaceModule):
        interface_template = 'interfaces/' + node.interface_name
        interface_code = self.render(interface_template)
        interface_ports = self.render(interface_template + '_port')
        return self.render('modules/InterfaceModule',
                           module_name=node.module_name,
                           interface_name=node.interface_name,
                           interface_ports=interface_ports,
                           interface_code=interface_code)

    def visit_FieldModule(self, node: FieldModule):
        return self.render('modules/FieldModule', module_name=node.module_name)

    def visit_InterruptModule(self, node: InterruptModule):
        return self.render('modules/InterruptModule', module_name=node.module_name)

    def visit_Port(self, node: Port):
        return self.render('Port', port=node)

    def visit_SignalDeclaration(self, node: SignalDeclaration):
        return self.render('SignalDeclaration', decl=node)
