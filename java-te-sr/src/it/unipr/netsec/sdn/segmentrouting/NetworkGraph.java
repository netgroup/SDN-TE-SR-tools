package it.unipr.netsec.sdn.segmentrouting;



import java.util.List;

import org.graphstream.graph.Edge;
import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.Path;
import org.graphstream.graph.implementations.SingleGraph;



/** A Network graph is an oriented graph with an attribute "capacity" associated to each edge.
 */
public class NetworkGraph extends SingleGraph {

	/** Whether working in debug mode */
	public static boolean DEBUG=false;

	/** Prints a debug message.
	 * @param str the string to be printed */
	protected static void debug(String str) {
		if (DEBUG) System.out.println("DEBUG: NetworkGraph: "+str);
	}

	/** Capacity attribute name */
	//public static final String CAPACITY="capacity";
	public static final String CAPACITY="edge_capacity";

	/** XYZ attribute name */
	private static final String XYZ="xyz";


	
	/** Creates a new network graph.
	 * @param id the graph id */
	public NetworkGraph(String id) {
		super(id);
	}


	/** Gets a copy.
	 * @return a copy of the graph */
	/*public Graph copy() {
		return copy(this,null,null,null);
	}*/

		
	/** Gets a copy.
	 * @param name the new graph name (<pre>null</pre> for copying the graph name)
	 * @param node_attributes array of node attributes to be copied (<pre>null</pre> for copying all node attributes)
	 * @param edge_attributes array of edge attributes to be copied (<pre>null</pre> for copying all edge attributes)
	 * @return a copy of the graph */
	public Graph copy(String name, String[] node_attributes, String[] edge_attributes) {
		return copy(this,name,node_attributes,edge_attributes);
	}

		
	/** Gets a copy of a given graph.
	 * @param graph the graph to be copied
	 * @return a copy of the graph */
	/*public static Graph copy(Graph graph) {
		return copy(graph,null,null,null);
	}*/

		
	/** Gets a copy of a given graph.
	 * @param graph the graph to be copied
	 * @param name the new graph name
	 * @return a copy of the graph */
	/*public static Graph copy(Graph graph, String name) {
		return copy(graph,name,null,null);
	}*/
	

	/** Gets a copy of a given graph.
	 * @param graph the graph to be copied
	 * @param name the new graph name (<pre>null</pre> for copying the graph name)
	 * @param node_attributes array of node attributes to be copied (<pre>null</pre> for copying all node attributes)
	 * @param edge_attributes array of edge attributes to be copied (<pre>null</pre> for copying all edge attributes)
	 * @return a copy of the graph */
	public static Graph copy(Graph graph, String name, String[] node_attributes, String[] edge_attributes) {
		debug("copy()");
		if (name==null) name=graph.getId();
		Graph g=new SingleGraph(name);
		for (Node node_i : graph.getNodeSet()) {
			Node n=g.addNode(node_i.getId());
			debug("copy(): add node: "+n);
			if (node_attributes!=null) for (String attribute_ij : node_attributes) n.addAttribute(attribute_ij,node_i.getAttribute(attribute_ij));
			else {
				for (String attribute_ij : node_i.getAttributeKeySet()) {
					n.addAttribute(attribute_ij,node_i.getAttribute(attribute_ij));
				}
			}		
		}
		for (Edge edge_i : graph.getEdgeSet()) {
			Edge e=g.addEdge(edge_i.getId(),edge_i.getSourceNode().getId(),edge_i.getTargetNode().getId(),edge_i.isDirected());
			debug("copy(): add edge: "+e);
			if (edge_attributes!=null) for (String attribute_ij : edge_attributes) e.addAttribute(attribute_ij,edge_i.getAttribute(attribute_ij));
			else {
				for (String attribute_ij : edge_i.getAttributeKeySet()) {
					e.addAttribute(attribute_ij,edge_i.getAttribute(attribute_ij));
				}			
			}
			
		}
		return g;
	}
	

	/** Adds a new node.
	 * @param node the node id
	 * @param the x coordinate
	 * @param the y coordinate */
	public void addNode(String node, double x, double y) {
		addNode(this,node,x,y);
	}

	
	/** Adds a new node to a graph.
	 * @param graph the graph
	 * @param node the node id
	 * @param the x coordinate
	 * @param the y coordinate */
	public static void addNode(Graph graph, String node, double x, double y) {
		graph.addNode(node).setAttribute(XYZ,x,y,0);
	}

	
	/** Adds a new one-way link (one edge).
	 * @param src the source node (root) of the edge
	 * @param dst the destination node of the edge
	 * @param capacity the link capacity */
	public void addLink(String src, String dst, double capacity) {
		addLink(this,src,dst,capacity);
	}

	
	/** Adds a new one-way link (one edge) to a graph.
	 * @param graph the graph
	 * @param src the source node (root) of the edge
	 * @param dst the destination node of the edge
	 * @param capacity the link capacity */
	public static void addLink(Graph graph, String src, String dst, double capacity) {
		String edge_id=src+dst;
		graph.addEdge(edge_id,src,dst,true);
		graph.getEdge(edge_id).setAttribute(CAPACITY,capacity);
	}

	
	/** Adds a new bidirectional link (two edges).
	 * @param node1 node 1
	 * @param node2 node 2
	 * @param capacity the link capacity */
	public void addBidirectionalLink(String node1, String node2, double capacity) {
		addBidirectionalLink(this,node1,node2,capacity);
	}

	
	/** Adds a new bidirectional link (two edges) to a graph.
	 * @param graph the graph
	 * @param node1 node 1
	 * @param node2 node 2
	 * @param capacity the link capacity */
	public static void addBidirectionalLink(Graph graph, String node1, String node2, double capacity) {
		addLink(graph,node1,node2,capacity);
		addLink(graph,node2,node1,capacity);
	}

	
	/** Gets a path.
	 * @param edges the graph edges that compose the path */
	public Path getPath(String[] edges) {
		return getPath(this,edges);
	}

	
	/** Gets a path within a graph.
	 * @param g the graph
	 * @param edges the graph edges that compose the path */
	public static Path getPath(Graph g, String[] edges) {
		Path path=new Path();
		Node src=g.getEdge(edges[0]).getSourceNode();
		path.setRoot(src);
		Node dst=src;
		for (String edge : edges) {
			Edge e=g.getEdge(edge);
			src=e.getSourceNode();
			if (dst!=src) throw new RuntimeException("Cannot append edge "+e+" to the path "+path+")");
			// else
			path.add(e);
			dst=e.getTargetNode();
		}
		return path;
	}


	/** Gets the source/first node (root) of a path.
	 * @param path the path */
	public static Node getPathSource(Path path) {
		return path.getRoot();
	}


	/** Gets the destination/last node (target) of a path.
	 * @param path the path */
	public static Node getPathDestination(Path path) {
		return path.getNodePath().get(path.size()-1);
	}


	/** Gets all nodes of a path.
	 * @param path the path */
	public static String[] getPathNodes(Path path) {
		String[] v=new String[path.size()];
		List<Node> nodes=path.getNodePath();
		for (int i=0; i<v.length; i++) {
			v[i]=nodes.get(i).getId();
		}
		return v;
	}


	/** Sets the capacity of a given bidirectional link (corresponding to a pair of edges).
	 * @param node1 node 1 of the link
	 * @param node2 node 2 of the link
	 * @param capacity the link capacity */
	/*public void setBidirectionalLinkCapacity(String node1, String node2, double capacity) {
		setBidirectionalLinkCapacity(this,node1,node2,capacity);
	}*/


	/** Sets the capacity of a given bidirectional link (corresponding to a pair of edges) of a graph.
	 * @param graph the graph
	 * @param node1 node 1 of the link
	 * @param node2 node 2 of the link
	 * @param capacity the link capacity */
	/*public static void setBidirectionalLinkCapacity(Graph graph, String node1, String node2, double capacity) {
		setLinkCapacity(graph,node1,node2,capacity);
		setLinkCapacity(graph,node2,node1,capacity);
	}*/


	/** Sets the capacity of a given link (edge).
	 * @param src the source node (root) of the link
	 * @param dst the destination node (target) of the link
	 * @param capacity the link capacity */
	/*public void setLinkCapacity(String src, String dst, double capacity) {
		setLinkCapacity(this,src,dst,capacity);
	}*/


	/** Sets the capacity of a given link (edge) of a graph.
	 * @param graph the graph
	 * @param src the source node (root) of the link
	 * @param dst the destination node (target) of the link
	 * @param capacity the link capacity */
	/*public static void setLinkCapacity(Graph graph, String src, String dst, double capacity) {
		Node s=graph.getNode(src);
		Node d=graph.getNode(dst);
		Edge e=s.getEdgeToward(d);
		setLinkCapacity(e,capacity);
	}*/


	/** Sets the capacity of a given link (edge).
	 * @param edge the link
	 * @param capacity the link capacity */
	/*public void setLinkCapacity(String edge, double capacity) {
		setLinkCapacity(this,edge,capacity);	
	}*/

	
	/** Sets the capacity of a given link (edge) of a graph.
	 * @param graph the graph
	 * @param edge the link
	 * @param capacity the link capacity */
	/*public static void setLinkCapacity(Graph graph, String edge, double capacity) {
		setLinkCapacity(graph.getEdge(edge),capacity);	
	}*/

	
	/** Sets the capacity of a given link (edge).
	 * @param edge the link
	 * @param capacity the link capacity */
	/*public static void setLinkCapacity(Edge edge, double capacity) {
		edge.setAttribute(CAPACITY,capacity);	
	}*/
	
}
