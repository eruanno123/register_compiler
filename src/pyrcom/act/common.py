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

# =============================================================================


class ACTVisitor:

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.default_visit)
        print('Visiting %s' % node.__class__.__name__)
        return visitor(node)

    def default_visit(self, node):
        if hasattr(node, '__getitem__'):
            return self._visit_iterable(node)
        elif hasattr(node, 'children'):
            return self._visit_iterable(node.children)
        else:
            return str(node)

    def _visit_iterable(self, iterable):
        ret = []
        for c in iterable:
            ret.append(self.visit(c))
        return '\n'.join(ret)

# =============================================================================


class ACTBuilder:
    """ Base class for all language specific ACT builders """

    def build(self, rdl_root):
        pass

# =============================================================================


class ACTNode:
    """ Abstract Component Tree node base class """

    def __repr__(self):
        return "ACTNode:%s <children:%d>" % (self.__class__.__name__, len(self.children))

    @property
    def children(self):
        return tuple()

# =============================================================================


class ACTComposite (ACTNode):
    """ Composite node. """

    def __init__(self, *args):
        self._children = args
        pass

    @property
    def children(self):
        return self._children

# =============================================================================


class GenericLayout (ACTComposite):
    def __init__(self, header=None, footer=None, *args):
        super(GenericLayout, self).__init__(args)
        self._header = header
        self._footer = footer

    @property
    def header(self):
        return self._header

    @property
    def footer(self):
        return self._footer
