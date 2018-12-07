# gml.py: pure Python 3 GML (Graph Modeling Language) parser with
#         no external dependencies

# Copyright (c) 2018 icasdri
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# NOTE: we assume GML disallow use of underscores in attribute names,
# therefore all of our object attributes that refer to Python objects (as
# opposed to the ones encoded by the GML itself) have underscores in their name

# NOTE: we use an extremely naive tokenization method that will destroy any
# whitespace character that is not exactly one single space in string
# attributes


class GMLError(Exception):
    pass


class Node:
    def __init__(self):
        # must have attribute id from GML
        self.is_anon = False
        self.forward_edges = []  # edges where this node is source
        self.backward_edges = []  # edges where this node is target

    def __str__(self):
        return 'node [\n{}\n]'.format('\n'.join(
            map(lambda x: '  {} {}'.format(x, repr(getattr(self, x)).replace("'", '"')),
                filter(lambda x: x in ('is_anon',) or '_' not in x, dir(self)))))

    def __repr__(self):
        return self.__str__()

class Edge:
    def __init__(self):
        # must have attributes source and target from GML
        self.source_node = None
        self.target_node = None

    def __str__(self):
        return 'edge [\n{}\n]'.format('\n'.join(
            map(lambda x: '  {} {}'.format(x, repr(getattr(self, x)).replace("'", '"')),
                filter(lambda x: '_' not in x, dir(self)))))

    def __repr__(self):
        return self.__str__()


class Graph:
    def __init__(self):
        self.graph_nodes = {}  # mapping id -> Node
        self.graph_edges = []  # set of Edge


class GMLParseError(GMLError):
    pass


class Parser:
    def __init__(self):
        # raw GML data (raw string split on whitespace)
        self._raw = []
        self._i = 0  # position (index) in self._raw

        self.graph = None

    def load_gml(self, path):
        with open(path) as infile:
            # NOTE: the split will destroy any spaces in string attributes
            self._raw = infile.read().strip().split()

        self._i = 0
        self.graph = Graph()

    def parse(self):
        if len(self._raw) == 0:
            raise GMLParseError('not loaded (must call load_gml before parse)')

        self._parse_graph()

    def _cur(self):
        if self._i >= len(self._raw):
            raise GMLParseError('[pos {}] unexpected end of file'.format(self._i))

        return self._raw[self._i]

    def _inc(self):
        self._i += 1

    def _parse_open_with_keyword(self, kw):
        if self._cur() != kw:
            raise GMLParseError('[pos {}] expected {} keyword, found: {}'.format(self._i, kw, self._cur()))
        self._inc()

        if self._cur() != '[':
            raise GMLParseError('[pos {}] expected opening [, found: {}'.format(self._i, self._cur()))
        self._inc()

    def _parse_graph(self):
        self._parse_open_with_keyword('graph')

        while self._cur() != ']':
            x = self._cur()
            if x == 'node':
                self._parse_node()
            elif x == 'edge':
                self._parse_edge()
            else:
                self._parse_attribute(self.graph)
        self._inc()

    def _parse_node(self):
        self._parse_open_with_keyword('node')

        node = Node()

        while self._cur() != ']':
            self._parse_attribute(node)
        self._inc()

        if not hasattr(node, 'id'):
            raise GMLParseError('[pos {}] node has no id'.format(self._i))

        nid = node.id

        if not isinstance(nid, int):
            raise GMLParseError('[pos {}] node has non-int id: {}'.format(self._i, nid))

        if nid in self.graph.graph_nodes:
            raise GMLParseError('[pos {}] redefinition of node id: {}'.format(self._i, nid))

        self.graph.graph_nodes[nid] = node

    def _parse_edge(self):
        self._parse_open_with_keyword('edge')

        edge = Edge()

        while self._cur() != ']':
            self._parse_attribute(edge)
        self._inc()

        if not hasattr(edge, 'source'):
            raise GMLParseError('[pos {}] edge has no source'.format(self._i))
        if not hasattr(edge, 'target'):
            raise GMLParseError('[pos {}] edge has no target'.format(self._i))

        if not isinstance(edge.source, int):
            raise GMLParseError('[pos {}] edge has non-int source: {}'.format(self._i, edge.source))
        if not isinstance(edge.target, int):
            raise GMLParseError('[pos {}] edge has non-int target: {}'.format(self._i, edge.target))

        for nid in (edge.source, edge.target):
            if nid not in self.graph.graph_nodes:
                node = Node()
                node.is_anon = True
                node.id = nid
                self.graph.graph_nodes[nid] = node

        edge.source_node = self.graph.graph_nodes[edge.source]
        edge.target_node = self.graph.graph_nodes[edge.target]

        edge.source_node.forward_edges.append(edge)
        edge.target_node.backward_edges.append(edge)

        self.graph.graph_edges.append(edge)

    # obj is object to add attribute to
    def _parse_attribute(self, obj):
        name = self._cur()
        if not name.isalnum():
            raise GMLParseError('[pos {}] attribute name is not alphanumeric: {}'.format(self._i, name))
        self._inc()

        val = self._cur()
        try:
            # try to parse val as int
            val = int(val, 10)
            self._inc()
            setattr(obj, name, val)
        except ValueError:
            # otherwise try to parse val as string
            if not val.startswith('"'):
                raise GMLParseError('[pos {}] attribute value is neither int nor str: {}'.format(self._i, val))

            val_l = []
            while not self._cur().endswith('"'):
                val_l.append(self._cur())
                self._inc()
            val_l.append(self._cur())  # capture closing one

            self._inc()

            val = ' '.join(val_l)  # unify
            val = val.strip('"')
            setattr(obj, name, val)
