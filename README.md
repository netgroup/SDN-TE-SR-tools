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
## Examples

### Small scale topology (Segment Routing paths deployment in the emulator)

In this example we parse a topology generated with Topology3D GUI, extract the set of flows (Virtual Leased Lines), allocate a Segment Routing path for each flow and then deploy the SR path on the Mininet emulator that emulates the topology.

### Large scale topology (no actual Segment Routing paths deployment in the emulator)

In this example we parse a graphml file that represents a large scale topology (>100 nodes), select a subset of nodes as edge nodes, generate the traffic demands (a set of flows among the edge nodes). Then we use a classical Traffic Engineering approach to select TE paths for the flows and then a optimal Segment Routing allocation algorithm to allocate SR path. We are able to evaluate percentage of allocated and rejected flows and metrics about the Segment Routing paths. We are not deploying the SR patch, because the topology is too big to be emulated in the Mininet emulator.

* using parsers-generators we parse a graphml file that represents a large scale topology (>100 nodes), select a subset of nodes as edge nodes, generate a catalogue of flows among the edge nodes, export the topology and the catalogue in json files

```
$ cd /home/user/workspace/sdn-te-sr-tools/parsers-generators
$ python parse_transform_generate.py --f graphml/Colt_2010_08-153N.graphml --in graphml --out nx --select_edge_nodes --generate_demands --access_node_prob 0.4 --t_rel_prob 0.2 --mean_num_flows 4 --max_num_flows 10 --link__to_t_rel_ratio 10  
```

* using java-te-sr we allocate the flows on the topology with a classical Traffin Engineering (TE) approach, then we take in input the selected TE-paths and allocate the SR paths
