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

from jinja2.exceptions import TemplateNotFound

# =============================================================================


class PyrcomError(Exception):
    """ Base class for all Pyrcom errors """

    def __init__(self, message=None):
        super(PyrcomError, self).__init__(message)

    @property
    def message(self):
        if self.args:
            message = self.args[0]
            if message is not None:
                return message


# =============================================================================


# class PyrcomNestedException(Exception):
#     """ Base class for exception that have 'inner' exception """

#     def __init__(self, message=None, inner_exception=None):
#         super(PyrcomNestedException, self).__init__(message)
#         self._inner_error = inner_exception


#     @property
#     def inner_exception(self):
#         return self._inner_exception

# =============================================================================


class CodegenError(PyrcomError):
    def __init__(self, message, node=None):
        super(CodegenError, self).__init__(message)
        self._affected_node = node

    def __str__(self):
        msg = self.message
        if self._affected_node:
            msg = "%s [Node: %s]" % (msg, self._affected_node)
        return msg

# =============================================================================


class CodegenTemplateError(PyrcomError):
    """ Code generation template error - mostly from Jinja2 subsystem. """

    def __init__(self, message=None):
        if not message:
            if hasattr(self, '__cause__'):
                if (self.__cause__, TemplateNotFound):
                    message = "Could not find template."
        super(CodegenTemplateError, self).__init__(message)
