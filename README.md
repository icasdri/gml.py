# gml.py

`gml.py` is a [Graph Modeling Language (GML)](https://en.wikipedia.org/wiki/Graph_Modelling_Language) parser for Python 3 with no external dependencies.

## Quickstart

```python3
import gml

# create a parser, load a file, and parse it!
parser = gml.Parser()
parser.load_gml('/path/to/mygraph.gml')
parser.parse()

# retrieve the resulting graph
graph = parser.graph

# access nodes of the graph
graph.graph_nodes  # dict of id -> Node objects

# access edges of the graph
graph.graph_edges  # list of Edge objects

# access attributes of a node or edge directly
node = graph.graph_nodes[0]
edge = graph.graph_edges[0]

node.id  # the id of this node
edge.source  # the source id of this edge

# special attributes on Nodes
node.is_anon  # whether or not this node actually appeared as a node block
              # in the input GML (or if it was inferred, via edge source/targets)
              # True if inferred, False if actually appeared
node.forward_edges  # list of Edge objects whose source is this node
node.backward_edges  # list of Edge objects whose target is this node

# special attributes on Edges
edge.source_node  # Node object corresponding to edge.source (which is an id)
edge.target_node  # Node object corresponding to edge.target (which is an id)
```

## Notes

* The parser assumes that the input GML does not use of underscores in
attribute names. This means that all object attributes on `Node`s and `Edge`s
that refer to Python objects (as opposed to the ones encoded by the GML itself)
have underscores in their name.
* The parser we uses a naive tokenization method that will destroy any
whitespace character that is not exactly one single space that occur in string
attribute values.

## License

MIT (see top of `gml.py` for full license text)
