import pytest

from systemrdl import RDLCompileError
from systemrdl.messages import MessagePrinter
from pyrcom.rc import RegisterCompiler

from pyrcom.sv.codegen import ASTCodeGenerator
from pyrcom.sv.ast import *


class Cfg:
    def __init__(self):
        self.incl_search_paths = ['examples/example_01/doc']
        self.top_def_name = None
        self.skip_not_present = False
        self.warning_flags = {'missing-reset': False}
        self.src_files = ['examples/example_01/i2c.rdl']


def test_nonExistingFile():
    compiler = RegisterCompiler(MessagePrinter(), Cfg())
    compiler.compile()


def test_astGenerator():

    sens = Sens(Identifier('CLK'), type='posedge')
    senslist = SensList([sens])

    assign_count_true = NonblockingSubstitution(
        Lvalue(Identifier('count')),
        Rvalue(IntConst('0')))
    if0_true = Block([assign_count_true])

    # count + 1
    count_plus_1 = Plus(Identifier('count'), IntConst('1'))
    assign_count_false = NonblockingSubstitution(
        Lvalue(Identifier('count')),
        Rvalue(count_plus_1))
    if0_false = Block([assign_count_false])

    if0 = IfStatement(Identifier('RST'), if0_true, if0_false)
    statement = Block([if0])
    always = Always(senslist, statement)

    cgen = ASTCodeGenerator()
    print(cgen.visit(always), file=sys.stderr)
