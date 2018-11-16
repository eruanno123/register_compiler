import pytest

from systemrdl import RDLCompileError
from systemrdl.messages import MessagePrinter
from pyrcom.rc import RegisterCompiler


class Cfg:
    def __init__(self):
        self.incl_search_paths = ['examples/example_01/doc']
        self.top_def_name = None
        self.skip_not_present = False
        self.warning_flags = {'missing-reset': False}
        self.src_files = ['examples/example_01/i2c.rdl']


def test_basicCompileNoError():

    cfg = {
        'incl_search_paths': ['examples/example_01/doc'],
        'warning_flags': {'all': True, 'missing-reset': False},
        'src_files': ['examples/example_01/i2c.rdl']
    }

    compiler = RegisterCompiler(**cfg)
    compiler.compile()
