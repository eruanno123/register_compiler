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

    def __init__(self, cfg):
        self.src_files = cfg.src_files
        self.incl_search_paths = cfg.incl_search_paths

    def compile(self):
        rdlc = RDLCompiler()

        for input_file in self.src_files:
            rdlc.compile_file(input_file, self.incl_search_paths)

        root = rdlc.elaborate()

        walker = RDLWalker(unroll=True)
        listener = RegisterTreeExtractionListener()
        walker.walk(root, listener)


if __name__ == '__main__':
    src_files = sys.argv[1:]

    # Create an instance of the compiler
    compiler = RegisterCompiler(src_files)

    try:
        compiler.compile()
    except RDLCompileError:
        sys.exit(1)
