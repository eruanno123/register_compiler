import pytest

from systemrdl import RDLCompileError
from register_compiler.rc import MyCompiler


def test_nonExistingFile():
    with pytest.raises(FileNotFoundError):
        compiler = MyCompiler(["non_existing_file"])
        compiler.compile()
