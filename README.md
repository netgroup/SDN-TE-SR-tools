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

* Set ENABLE_SEGMENT_ROUTING = True in nodes.py of the project Dreamer-Mininet-Extensions (Line 32)
* In the Topology3D GUI load the example topology: from the top bar "Topology" menu, select "Import topology from file"
Choose the file /home/user/workspace/sdn-te-sr-tools/parsers-generators/t3d/small-topo2-4-vll.t3d
* Deploy the topology: In the left frame, from the Deployment menu, select Deploy.
In the deployment window on the bottom, type deploy and then press enter.
* Identify the controller IP address from the output of the deployment script and run the controller from a console in your VM (root password is "root"):
```
$ ssh -X root@10.255.245.1
# ./ryu_start.sh
```
(or manually:)
```
# cd /home/user/workspace/dreamer-ryu/ryu/app
# ryu-manager rest_topology.py ofctl_rest.py --observe-links
```
* Generates the flow catalogue to be handed over to the SR allocation algorithm (properly replace the controller IP address), from a second console in your VM, then move the files in topology and flows folders of java-te-sr project
```
$ cd /home/user/workspace/Mantoo-scripts-and-readme
$ ./generate_topo_and_flow_cata.sh 10.255.245.1:8080
```
(or manually:)
```
$ cd /home/user/workspace/sdn-te-sr-tools/parsers-generators
$ python parse_transform_generate.py --in ctrl_ryu --out nx --generate_flow_cata_from_vll_pusher_cfg --controller 10.255.245.1:8080 
$ mv flow_catalogue.json ../java-te-sr/flow/
$ mv links.json ../java-te-sr/topology/
$ mv nodes.json ../java-te-sr/topology/
```
* Check the generated flow catalogue
```
$ cat /home/user/workspace/sdn-te-sr-tools/parsers-generators/flow_catalogue.json
```
* Run the SR allocation algorithm
 * Open Eclipse (from the Applications Menu at the top left, select Development->Eclipse)
 * set Main parameters (right click on UniPR-SDN-TE-SR project, Run as-> Run Configurations, in the Arguments tab edit the Program arguments as follows) 
```
topo_in=topology/links.json
topo_out=topology/links.json.out
flows_in=flow/flow_catalogue.json
flows_out=flow/flow_catalogue.json.out
```
** Run (right click on UniPR-SDN-TE-SR project, Run as-> Run Configurations, click the Run button at the right bottom NB the Main class should be it.unipr.netsec.sdn.run.Main) - do not expect any message on the console, if everything is OK nothing is returned

* Move flow_catalogue.json.out to OSHI-SR-pusher and run sr_vll_pusher
```
$ cd /home/user/workspace/Mantoo-scripts-and-readme
$ ./sr_pusher_start.sh 10.255.245.1:8080 --add
```
(or manually:)
```
$ cd /home/user/workspace/sdn-te-sr-tools
$ mv java-te-sr/flow/flow_catalogue.json.out OSHI-SR-pusher/out_flow_catalogue.json
$ cd /home/user/workspace/sdn-te-sr-tools/OSHI-SR-pusher/
$ rm sr_vlls.json
$ ./sr_vll_pusher.py --controller 10.255.245.1:8080 --add
```

* Now you can ping over a VLL implemented using segment routing. For example ping from cer1 to cer9:
 * open a shell on cer1 (on the web GUI with CTRL-Left-Click on cer1 or with
```
ssh -X root@10.255.247.1
```
 * show the interfaces of cer1
```
ip a
```
 * ping to cer9 on the VLL
```
ping 10.0.14.2
```


### Large scale topology (no actual Segment Routing paths deployment in the emulator)

In this example we parse a graphml file that represents a large scale topology (>100 nodes), select a subset of nodes as edge nodes, generate the traffic demands (a set of flows among the edge nodes). Then we use a classical Traffic Engineering approach to select TE paths for the flows and then a optimal Segment Routing allocation algorithm to allocate SR path. We are able to evaluate percentage of allocated and rejected flows and metrics about the Segment Routing paths. We are not deploying the SR patch, because the topology is too big to be emulated in the Mininet emulator.

* using parsers-generators we parse a graphml file that represents a large scale topology (>100 nodes), select a subset of nodes as edge nodes, generate a catalogue of flows among the edge nodes, export the topology and the catalogue in json files, called nodes.json and links.json (for the topology) and flow_catalogue.json for the traffic demands

```
$ cd /home/user/workspace/sdn-te-sr-tools/parsers-generators
$ python parse_transform_generate.py --f graphml/Colt_2010_08-153N.graphml --in graphml --out nx --select_edge_nodes --generate_demands --access_node_prob 0.4 --t_rel_prob 0.2 --mean_num_flows 4 --max_num_flows 10 --link__to_t_rel_ratio 10  
```

* using java-te-sr we allocate the flows on the topology with a classical Traffin Engineering (TE) approach, then we take in input the selected TE-paths and allocate the SR paths
