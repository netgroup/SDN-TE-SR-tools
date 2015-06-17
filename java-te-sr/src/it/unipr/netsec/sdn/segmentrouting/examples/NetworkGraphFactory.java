package it.unipr.netsec.sdn.segmentrouting.examples;




import it.unipr.netsec.sdn.segmentrouting.NetworkGraph;

import org.graphstream.graph.Graph;



/** Collection of static methods for creating some networks.
 */
public class NetworkGraphFactory {

	/** Gets a test network graph of type 1.
	 * It is a square, with two triangles on top of two opposite sides, with two links on top of the vertexes of the two triangles.
	 * @param name the graph name */
	public static Graph getTestNetworkGraph_1(String name) {
		NetworkGraph g=new NetworkGraph(name); 
		g.addNode("A",2,1);
		g.addNode("B",4,2);
		g.addNode("C",6,2);
		g.addNode("D",4,0);
		g.addNode("E",6,0);
		g.addNode("F",8,1);
		g.addNode("G",0,1);
		g.addNode("H",10,1);
		g.addBidirectionalLink("A","B",4.0);
		g.addBidirectionalLink("A","D",1.0);
		g.addBidirectionalLink("B","C",2.0);
		g.addBidirectionalLink("D","E",2.0);				
		g.addBidirectionalLink("B","D",1.0);				
		g.addBidirectionalLink("C","E",1.0);				
		g.addBidirectionalLink("C","F",1.0);				
		g.addBidirectionalLink("E","F",4.0);
		g.addBidirectionalLink("A","G",8.0);
		g.addBidirectionalLink("F","H",8.0);
		return g;
	}

	
	/** Gets a test network graph of type 2.
	 * It is a ring of six nodes.
	 * @param name the graph name */
	public static Graph getTestNetworkGraph_2(String name) {
		NetworkGraph g=new NetworkGraph(name); 
		g.addNode("A",0.0,0.866);
		g.addNode("B",0.5,0.866*2);
		g.addNode("C",1.5,0.866*2);
		g.addNode("D",2.0,0.866);
		g.addNode("E",1.5,0.0);
		g.addNode("F",0.5,0.0);
		g.addBidirectionalLink("A","B",1.0);
		g.addBidirectionalLink("B","C",1.0);
		g.addBidirectionalLink("C","D",1.0);				
		g.addBidirectionalLink("D","E",1.0);				
		g.addBidirectionalLink("E","F",1.0);				
		g.addBidirectionalLink("F","A",1.0);				
		return g;
	}

}
