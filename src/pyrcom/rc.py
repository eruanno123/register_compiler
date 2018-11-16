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

from systemrdl import RDLCompiler, RDLListener, RDLWalker, RDLCompileError
from systemrdl.node import FieldNode
from systemrdl.messages import *

from pyrcom.regtree import RegisterTree

import sys


# Define a listener that will print out the register model hierarchy
class RegisterTreeExtractionListener(RDLListener):
    def __init__(self):
        self.indent = 0
        self.regtree = ()

    def enter_Addrmap(self, node):
        print("Entering addrmap", node.get_path())

    def exit_Addrmap(self, node):
        print("Exiting addrmap", node.get_path())

    def enter_Reg(self, node):
        print("Entering register", node.get_path())

    def exit_Reg(self, node):
        print("Exiting register", node.get_path())

    def enter_Field(self, node):
        print("Entering field", node.get_path())

    def exit_Field(self, node):
        print("Exiting field", node.get_path())

    # def enter_Component(self, node):
    #     print("Entering component", node.get_path())

    # def exit_Component(self, node):
    #     print("Exiting component", node.get_path())


class RegisterCompiler:

    def __init__(self, printer=MessagePrinter(), **kwargs):
        """ Init compiler. TODO: doc parameters """

        self.printer = printer
        self.incl_search_paths = kwargs.pop('incl_search_paths', None)
        self.top_def_name = kwargs.pop('top_def_name', None)
        self.skip_not_present = kwargs.pop('skip_not_present', False)
        self.warning_flags = kwargs.pop('warning_flags', [])
        self.src_files = kwargs.pop('src_files', [])

    def print_message(self, severity, text, src_ref=None):
        """ Wrapper to printer.print_message allowing default `src_ref` """
        self.printer.print_message(severity, text, src_ref)

    def getWarningMask(self, warning_flags):
        w_bits = {
            'all': W_ALL,
            'missing-reset': W_MISSING_RESET,
            'implicit': W_IMPLICIT_ADDR | W_IMPLICIT_FIELD_POS,
            'implicit-addr': W_IMPLICIT_FIELD_POS,
            'implicit-field-pos': W_IMPLICIT_ADDR
        }
        mask = 0
        for wf, suppressed in warning_flags.items():
            bits = w_bits[wf]
            if suppressed:
                self.print_message(
                    "debug", str.format("suppress warning '{}'", wf))
                mask &= ~bits
            else:
                self.print_message(
                    "debug", str.format("enable warning '{}'", wf))
                mask |= bits
        return mask

    def compile(self):

        warning_mask = self.getWarningMask(self.warning_flags)
        self.print_message("debug", str.format(
            "warning_mask: {0}", warning_mask), None)

        rdlc = RDLCompiler(message_printer=self.printer,
                           warning_flags=warning_mask)

        for input_file in self.src_files:
            self.print_message(
                "info", str.format("Compiling {0} ...", input_file))
            rdlc.compile_file(input_file, self.incl_search_paths)

        self.print_message("info", "Elaborating ...")
        root = rdlc.elaborate(top_def_name=self.top_def_name)

        return root
        # walker = RDLWalker(
        #     unroll=True, skip_not_present=self.skip_not_present)
        # listener = RegisterTreeExtractionListener()
        # walker.walk(root, listener)
