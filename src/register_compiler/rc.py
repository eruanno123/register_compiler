#!/usr/bin/python


from systemrdl import RDLCompiler, RDLListener, RDLWalker, RDLCompileError
from systemrdl.node import FieldNode

import sys


# Define a listener that will print out the register model hierarchy
class MyModelPrintingListener(RDLListener):
    def __init__(self):
        self.indent = 0

    def enter_Component(self, node):
        if not isinstance(node, FieldNode):
            print("\t"*self.indent, node.get_path_segment(), node.absolute_address
                  )
            self.indent += 1

    def enter_Field(self, node):
        # Print some stuff about the field
        bit_range_str = "[%d:%d]" % (node.inst.high, node.inst.low)
        sw_access_str = "sw=%s" % node.get_property("sw").name
        brief = "%s" % node.get_property("brief")
        desc = "%s" % node.get_property("desc")
        print("\t"*self.indent, bit_range_str,
              node.get_path_segment(), sw_access_str, brief, desc.strip())

    def exit_Component(self, node):
        if not isinstance(node, FieldNode):
            self.indent -= 1


class MyCompiler:

    def __init__(self, input_files):
        self.input_files = input_files

    def compile(self):
        # Create an instance of the compiler
        rdlc = RDLCompiler()

        # Compile all the files provided
        for input_file in self.input_files:
            rdlc.compile_file(input_file)

        # Elaborate the design
        root = rdlc.elaborate()

        # Traverse the register model!
        walker = RDLWalker(unroll=True)
        listener = MyModelPrintingListener()
        walker.walk(root, listener)


if __name__ == '__main__':
    input_files = sys.argv[1:]

    # Create an instance of the compiler
    compiler = MyCompiler(input_files)

    try:
        compiler.compile()
    except RDLCompileError:
        sys.exit(1)
