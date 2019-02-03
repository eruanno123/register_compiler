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
from pyrcom.exceptions import PyrcomError
from pyrcom.codegen.systemverilog import SystemVerilogEmitter, SystemVerilogBuilder
from systemrdl.messages import MessagePrinter, Severity
from systemrdl.messages import RDLCompileError

import argparse
import collections

class RDLArgumentError(RDLCompileError):
    """ Command line argument error """
    pass


class RDLMessagePrinter(MessagePrinter):

    def __init__(self):
        self.severity_desc = { Severity.FATAL: True, Severity.ERROR : True, Severity.WARNING : True, Severity.NONE : False }

    def enable(self, severity):
        self.severity_desc[severity] = True

    def disable(self, severity):
        self.severity_desc[severity] = False

    def print_message(self, severity, text, src_ref=None):

        if severity in self.severity_desc and self.severity_desc[severity]:
            if (severity == Severity.FATAL or severity == Severity.ERROR):
                # use built in support for these severities
                lines = self.format_message(severity, text, src_ref)
                self.emit_message(lines)
            else:
                # just emit simple message
                self.emit_message([str.format("{0}: {1}", severity, text)])


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
            '-v', '--verbose',
            action='store_true',
            dest='verbose_mode',
            help="Enable verbose compilation status print out."
        )
        ap.add_argument(
            '--debug',
            action='store_true',
            dest='debug_mode',
            help="Enable compiler debug mode (with yet more compiler status print out)."
        )
        ap.add_argument(
            '-O', '--output',
            metavar='<file>',
            type=str,
            required=True,
            dest='output_path',
            help="Compile output artifact."
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
        suppressed = collections.OrderedDict()

        # Note: OrderedDict is useful to preserve sane behavior in something
        # like: "-Wall -Wno-missing-reset"

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

            if cfg.verbose_mode:
                self.printer.enable(Severity.NONE)

            compiler = RegisterCompiler(
                printer=self.printer,
                incl_search_paths=cfg.incl_search_paths,
                top_def_name=cfg.top_def_name,
                skip_not_present=cfg.skip_not_present,
                warning_flags=cfg.warning_flags,
                src_files=cfg.src_files
            )

            self.printer.print_message(Severity.NONE, "Start code compilation ...")
            rdl_root = compiler.compile()

            # TODO: select and configure generator from config
            self.printer.print_message(Severity.NONE, "Generating ...")
            language_config = {'design_name' : 'mydev'}
            code_generator = SystemVerilogEmitter("sv", language_config, printer=self.printer, template_suffix=".sv")
            language_builder = SystemVerilogBuilder(language_config, printer=self.printer)
            code = code_generator.generate_code(language_builder, rdl_root)

            self.printer.print_message(Severity.NONE, "Writing output ...")
            with open(cfg.output_path, "w") as fd:
                fd.write(code)

        except (RDLCompileError, PyrcomError) as e:
            message = str(e)
            if hasattr(e, '__cause__') and e.__cause__:
                message = "%s Details: %s" % (message, e.__cause__)
            self.printer.print_message(Severity.ERROR, message, None)



if __name__ == "__main__":
    RDLCommandLineRunner(RDLMessagePrinter()).run()
