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

from pyrcom.act.common import ACTNode, ACTComposite
from pyrcom.exceptions import CodegenError

# =============================================================================
# Abstract Component Tree classes
# =============================================================================

# Name alias
Composite = ACTComposite

# =============================================================================


class LogicalGroup (Composite):
    """ Represent logically grouped code components """

    def __init__(self, level, description="", *args):
        super(LogicalGroup, self).__init__(args)
        self._level = level
        self._description = description

    @property
    def level(self):
        return self._level

    @property
    def description(self):
        return self._description


# =============================================================================


class Range (ACTNode):
    """ Represents SystemVerilog style bit vector range """

    def __init__(self, high=0, low=0):
        self._high = high
        self._low = low

    def __repr__(self):
        return str(self._high) if (self._high == self._low) \
            else str.format("{0}:{1}", self._high, self._low)

    def __str__(self):
        return '[' + repr(self) + ']'

    def shift(self, offset):
        return Range(self._high+offset, self._low+offset)

    def shift_to_zero(self):
        return self.shift(-self._low)

    @property
    def high(self):
        return self._high

    @property
    def low(self):
        return self._low

# =============================================================================


class Port (ACTNode):
    """ Represents port declaration in SystemVerilog module definition """

    def __init__(self, name, direction="input", range=None):
        self._name = name
        self._direction = direction
        self._range = range
        self._sanity_check()

    def __repr__(self):
        return str.format(
            "{0} [{1}] {2}" if self._range else "{0} {2}",
            self._direction, self._range, self._name
        )

    def _sanity_check(self):
        expectedDirection = ["input", "output", "inout"]
        if self._direction not in expectedDirection:
            raise CodegenError(str.format(
                "Unknown direction '{0}'. Expected values: '{1}'", self._direction, expectedDirection), self)

    @property
    def name(self):
        return self._name

    @property
    def direction(self):
        return self._direction

    @property
    def range(self):
        return self._range

# =============================================================================


class SignalDeclaration (ACTNode):
    """ Represents logic or wire declaration """

    def __init__(self, name, kind="wire", range=None):
        self._name = name
        self._kind = kind
        self._range = range
        self._sanity_check()

    def __repr__(self):
        return str.format(("{0!r} [{1!r}] {2!r};" if self._range else "{0!r} {2!r};"),
                          self._kind, self._range, self._name)

    def _sanity_check(self):
        expectedKind = ["reg", "logic", "wire"]
        if self._kind not in expectedKind:
            raise CodegenError(str.format(
                "Unknown declaration type '{0}'. Expected values: '{1}'", self._kind, expectedKind), self)

    @property
    def kind(self):
        return self._kind

    @property
    def range(self):
        return self._range

    @property
    def name(self):
        return self._name

# =============================================================================

class Net (ACTNode):
    """ Represents a SystemVerilog net """
    def __init__(self, name, range=None):
        self._name = name
        self._range = range

    def __repr__(self):
        return str.format("{0!r}('{1!r}','{2!r}", self.__class__, self._name, self._range)

    @property
    def name(self):
        return self._name

    @property
    def range(self):
        return self._range

    @property
    def width(self):
        r = self._range
        return r.width if r else 1

# =============================================================================


class Assignment (ACTNode):

    def __init__(self,
                 lhs, rhs,
                 lhs_range=None,
                 rhs_range=None,
                 is_continuous=False):
        self._lhs = lhs
        self._rhs = rhs
        self._lhs_range = lhs_range
        self._rhs_range = rhs_range
        self._is_continuous = is_continuous
        self._sanity_check()

    def _sanity_check(self):
        if (self.lhs_width != self.rhs_width):
            raise CodegenError(str.format(
                "Assignment width mismatch: left side expects {} bits, but got {}",
                self.lhs_width, self.rhs_width), self)

    def __repr__(self):
        rl = str(self._lhs or '')
        rr = str(self._rhs or '')
        return str.format("{0}{}{} = {}{}",
            'assign' if self._is_continuous else '',
            self._lhs, rl,
            self._rhs, rr)

    @property
    def lhs(self):
        return self._lhs

    @property
    def lhs_range(self):
        return self._lhs_range

    @property
    def lhs_width(self):
        r = self._lhs_range
        return r.width if r else 1

    @property
    def rhs(self):
        return self._rhs

    @property
    def rhs_range(self):
        return self._rhs_range

    @property
    def rhs_width(self):
        r = self._rhs_range
        return r.width if r else 1


# =============================================================================


# =============================================================================

# =============================================================================


class FieldInstance (ACTNode):

    def __init__(self, parent_reg_name, field_name, field_range=Range(), reset_mask=0, reset_value=0):
        self._parent_reg_name = parent_reg_name
        self._field_name = field_name
        self._field_range = field_range
        self._field_reset_mask = reset_mask
        self._field_reset_value = reset_value

    @property
    def parent_reg_name(self):
        return self._parent_reg_name

    @property
    def field_name(self):
        return self._field_name

    @property
    def field_range(self):
        return self._field_range

    @property
    def field_width(self):
        return self._field_range.high-self._field_range.low+1

    @property
    def field_reset_mask(self):
        return self._field_reset_mask

    @property
    def field_reset_value(self):
        return self._field_reset_value


# =============================================================================


class FieldBypass (ACTNode):

    def __init__(self, parent_reg_name, field_name, field_range=Range()):
        self._parent_reg_name = parent_reg_name
        self._field_name = field_name
        self._field_range = field_range

    @property
    def parent_reg_name(self):
        return self._parent_reg_name

    @property
    def field_name(self):
        return self._field_name

    @property
    def field_range(self):
        return self._field_range

# =============================================================================


class InterruptInstance (ACTNode):
    def __init__(self, intr_name):
        self._intr_name = intr_name

    @property
    def intr_name(self):
        return self._intr_name

# =============================================================================


class ModuleBase (ACTNode):
    """ Represents SystemVerilog module """

    def __init__(self, module_name):
        self._module_name = module_name

    @property
    def module_name(self):
        return self._module_name

# =============================================================================


class TopModule (ModuleBase):
    def __init__(self, module_name,
                 interface_name,
                 hw_ports=[]):
        super(TopModule, self).__init__(module_name)
        self._interface_name = interface_name
        self._hw_ports = hw_ports

    @property
    def hw_ports(self):
        return self._hw_ports

    @property
    def interface_name(self):
        return self._interface_name

# =============================================================================


class BackendModule (ModuleBase):

    def __init__(self, module_name,
                 hw_ports=[],
                 backend_signal_declarations=[],
                 backend_instantiation=[],
                 write_select_decoder=None):
        super(BackendModule, self).__init__(module_name)
        self._hw_ports = hw_ports
        self._backend_signal_declarations = backend_signal_declarations
        self._backend_instantiation = backend_instantiation
        self._write_select_decoder = write_select_decoder

    @property
    def hw_ports(self):
        return self._hw_ports

    @property
    def backend_signal_declarations(self):
        return self._backend_signal_declarations

    @property
    def backend_instantiation(self):
        return self._backend_instantiation

    @property
    def write_select_decoder(self):
        return self._write_select_decoder

# =============================================================================


class InterfaceModule (ModuleBase):
    def __init__(self, module_name,
                 interface_name):
        super(InterfaceModule, self).__init__(module_name)
        self._interface_name = interface_name

    @property
    def interface_name(self):
        return self._interface_name

# =============================================================================


class FieldModule (ModuleBase):
    def __init__(self, module_name):
        super(FieldModule, self).__init__(module_name)

# =============================================================================


class InterruptModule (ModuleBase):
    def __init__(self, module_name):
        super(InterruptModule, self).__init__(module_name)


# =============================================================================

class SelectDecoder (ACTNode):

    def __init__(self, address_map):
        """ address_map keeps mapping between address and selected signal """
        self._address_map = address_map

    @property
    def address_map(self):
        return self._address_map
