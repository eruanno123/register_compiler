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

import argparse


def getArgumentParser():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-I', '--include-dir',
        metavar='dir',
        type=str,
        action='append',
        dest='incl_search_paths',
        help="Include search path."
    )
    ap.add_argument(
        'src_files',
        metavar='src',
        nargs='+',
        type=str,
        help="List of input files"
    )
    return ap


def main():

    parser = getArgumentParser()
    cfg = parser.parse_args()

    print(cfg)
    compiler = RegisterCompiler(cfg)
    compiler.compile()


if __name__ == "__main__":
    main()
