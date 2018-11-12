import pytest

from systemrdl import RDLCompileError
from register_compiler.rc import MyCompiler

from register_compiler.sv.codegen import ASTCodeGenerator


def test_nonExistingFile():
    with pytest.raises(FileNotFoundError):
        compiler = MyCompiler(["non_existing_file"])
        compiler.compile()


def test_astGenerator():
    cgen = ASTCodeGenerator()
