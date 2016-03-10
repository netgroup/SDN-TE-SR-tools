# SDN-TE-SR-tools
Tools for SDN based Traffic Engineering and Segment Routing

It includes
* parsers-generators
* java-te-sr
* OSHI-SR-pusher
 
## parsers-generators
It is a collection of tools for:

1. parsing topologies and converting them among different formats
2. generating traffic demands and evaluate some metrics 

We consider two examples:

Example 1)
1.1) using parsers-generators we parse a graphml file that represents a large scale topology (>100 nodes), select a subset of nodes as edge nodes, generate a catalogue of flows among the edge nodes, export the topology and the catalogue in json files
1.2) using java-te-sr we allocate the flows on the topology with a classical Traffin Engineering (TE) approach, then we take in input the selected TE-paths .
[to be continued)
