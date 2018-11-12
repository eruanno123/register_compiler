import pytest

from systemrdl import RDLCompileError
from pyrcom.rc import RegisterCompiler

from pyrcom.sv.codegen import ASTCodeGenerator


def test_nonExistingFile():
    with pytest.raises(FileNotFoundError):
        compiler = RegisterCompiler(["non_existing_file"])
        compiler.compile()


def test_astGenerator():
    cgen = ASTCodeGenerator()
