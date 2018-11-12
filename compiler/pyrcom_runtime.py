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

# Python Register Compiler - reference implementation

from pyrcom.rc import RegisterCompiler
from systemrdl.messages import MessagePrinter

import argparse


class RDLArgumentError(Exception):
    """ Command line argument error """
    pass


class RDLMessagePrinter(MessagePrinter):
    def print_message(self, severity, text, src_ref=None):

        if (severity == "debug"):
            self.emit_message(["debug: " + text])
        else:
            lines = self.format_message(severity, text, src_ref)
            self.emit_message(lines)


class RDLCommandLineRunner:

    def __init__(self, printer):
        self.printer = printer
        pass

    def createArgumentParser(self):
        ap = argparse.ArgumentParser()
        ap.add_argument(
            '-I', '--include-dir',
            metavar='<dir>',
            type=str,
            action='append',
            dest='incl_search_paths',
            help="Include search path."
        )
        ap.add_argument(
            '-t', '--top',
            metavar='<addrmap>',
            type=str,
            dest='top_def_name',
            help="Explicitly choose which addrmap in the root namespace will be the top-level component. "
            "If unset, the last addrmap defined will be chosen"
        )
        ap.add_argument(
            '-s', '--skip-not-present',
            action='store_true',
            dest='skip_not_present',
            help="If set, compiler skips nodes whose ‘ispresent’ property is set to False."
        )
        ap.add_argument(
            '-W',
            metavar='<warning/no-warning>',
            type=str,
            action='append',
            dest='warning_spec',
            help="Enable warnings (-Wwarning-name) or disable (-Wno-warning-name)"
        )
        ap.add_argument(
            'src_files',
            metavar='src',
            nargs='+',
            type=str,
            help="List of input files"
        )
        return ap

    def warnAboutDuplicateFlag(self, flagName, curSuppressed, prevSuppressed):
        state = {False: '', True: 'no-'}
        self.printer.print_message("warning", str.format(
            "duplicated warning flag '-W{1}{0}'", flagName, state[curSuppressed]), None)
        if curSuppressed != prevSuppressed:
            self.printer.print_message("warning", str.format(
                "current flag '-W{1}{0}' will supersede previous flag '-W{2}{0}", flagName, state[curSuppressed], state[prevSuppressed]), None)

    def getWarningFlags(self, warning_spec):

        supported = ['all', 'missing-reset', 'implicit',
                     'implicit-addr', 'implicit-field-pos']
        suppressed = dict()

        if warning_spec:
            for flag in warning_spec:  # type: str
                isNo = flag.startswith('no-')
                flagName = flag[3:] if isNo else flag

                if flagName not in supported:
                    raise RDLArgumentError(str.format(
                        "Unsupported warning flag '-W{0}'", flag))

                if flagName in suppressed:
                    self.warnAboutDuplicateFlag(
                        flagName, suppressed[flagName], isNo)
                suppressed[flagName] = isNo
        return suppressed

    def run(self):

        try:
            parser = self.createArgumentParser()
            cfg = parser.parse_args()
            cfg.warning_flags = self.getWarningFlags(cfg.warning_spec)

            compiler = RegisterCompiler(self.printer, cfg)
            compiler.compile()
        except RDLArgumentError as e:
            self.printer.print_message("error", str(e), None)


if __name__ == "__main__":
    RDLCommandLineRunner(RDLMessagePrinter()).run()
