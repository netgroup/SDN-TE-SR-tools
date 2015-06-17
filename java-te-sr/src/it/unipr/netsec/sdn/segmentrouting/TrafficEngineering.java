package it.unipr.netsec.sdn.segmentrouting;



import org.graphstream.graph.Edge;
import org.graphstream.graph.Graph;
import org.graphstream.graph.Path;

import java.util.Hashtable;



/** Traffic engineering onto a given network.
 *  It allows the adding and removing of traffic flows. 
 */
public class TrafficEngineering {

	/** Whether working in debug mode */
	public static boolean DEBUG=false;

	/** Array of node attributes used in TE computation */
	private static String[] NODE_ATTRIBUTES=new String[]{};

	/** Array of edge attributes used in TE computation */
	private static String[] EDGE_ATTRIBUTES=new String[]{NetworkGraph.CAPACITY};



	/** Prints a debug message.
	 * @param str the string to be printed */
	protected static void debug(String str) {
		if (DEBUG) System.out.println("DEBUG: TrafficEngineering: "+str);
	}

	
	/** Network with original capacity */
	Graph network;
	
	/** Network with remaining capacity */
	Graph residue_network;

	/** allocated traffic paths */
	Hashtable<TrafficFlow,Path> allocated_paths=new Hashtable<TrafficFlow,Path>();



	/** Creates a new TrafficEngineering.
	 * @param network the network */
	public TrafficEngineering(Graph network) {
		this.network=network;
		this.residue_network=NetworkGraph.copy(network,network.getId()+" residue",NODE_ATTRIBUTES,EDGE_ATTRIBUTES);
	}

	
	/** Gets the network with original capacity.
	 * @return the network */
	public synchronized Graph getOriginalNetwork() {
		return network;
	}


	/** Gets the network with remaining capacity.
	 * @return the network */
	public synchronized Graph getResidueNetwork() {
		return residue_network;
	}


	/** Gets the allocated path for a given path.
	 * @param flow the traffic flow
	 * @return the allocates path */
	public synchronized Path getAllocatedPath(TrafficFlow flow) {
		return allocated_paths.get(flow);
	}


	/** Adds a new traffic flow.
	 * @param flow the traffic flow
	 * @return <i>true</i> if it succeeded */
	public synchronized boolean addFlow(TrafficFlow flow) {
		debug("addFlow(): flow: "+flow);
		Graph pruned_graph=NetworkGraph.copy(network,network.getId()+" pruned",NODE_ATTRIBUTES,EDGE_ATTRIBUTES);
		double bandwidth=flow.getBandwidth();
		for (Edge edge_i : residue_network.getEdgeSet()) {
			if (((double)edge_i.getAttribute(NetworkGraph.CAPACITY))<bandwidth) pruned_graph.removeEdge(edge_i.getId());
		}
		Path path=SegmentRouting.getNaturalPath(pruned_graph,flow.getSource(),flow.getDestination());
		debug("addFlow(): path: "+path);
		if (path!=null && path.size()>0) {
			addFlow(flow,path);
			return true;
		}
		else return false;
	}


	/** Adds a new traffic flow.
	 * @param flow the traffic flow
	 * @param path the traffic path */
	public synchronized void addFlow(TrafficFlow flow, Path path) {
		allocated_paths.put(flow,path);
		double bandwidth=flow.getBandwidth();
		for (Edge path_edge : path.getEdgeSet()) {
			Edge network_edge=residue_network.getEdge(path_edge.getId());
			double residue_capacity=network_edge.getAttribute(NetworkGraph.CAPACITY);
			if (bandwidth>residue_capacity) throw new RuntimeException("Flow bandwidth for path "+path+" exceeds the residue capacity of link "+network_edge.getId()+" ("+bandwidth+" > "+residue_capacity+")");
			residue_capacity-=bandwidth;
			network_edge.setAttribute(NetworkGraph.CAPACITY,residue_capacity);
		}
	}


	/** Removes a traffic flow.
	 * @param flow the traffic flow */
	public synchronized void removeFlow(TrafficFlow flow) {
		debug("removeFlow(): flow: "+flow);
		Path path=allocated_paths.get(flow);
		double bandwidth=flow.getBandwidth();
		for (Edge path_edge : path.getEdgeSet()) {
			Edge network_edge=residue_network.getEdge(path_edge.getId());
			double residue_capacity=network_edge.getAttribute(NetworkGraph.CAPACITY);
			residue_capacity+=bandwidth;
			network_edge.setAttribute(NetworkGraph.CAPACITY,residue_capacity);
		}
		allocated_paths.remove(flow);
	}


	@Override
	public synchronized String toString() {
		StringBuffer sb=new StringBuffer();
		sb.append('[');
		boolean first_edge=true;
		for (Edge edge : network.getEdgeSet()) {
			String edge_id=edge.getId();
			Edge residue_edge=residue_network.getEdge(edge_id);
			if (first_edge) first_edge=false;
			else sb.append(',');
			sb.append(edge_id).append(':');
			sb.append(residue_edge.getAttribute(NetworkGraph.CAPACITY));
			sb.append('/').append(edge.getAttribute(NetworkGraph.CAPACITY));
		}
		sb.append(']');
		return sb.toString();
	}

}
