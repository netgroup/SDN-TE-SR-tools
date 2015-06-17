package it.unipr.netsec.sdn.segmentrouting;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import org.graphstream.algorithm.Dijkstra;
import org.graphstream.graph.Edge;
import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.Path;

/** Collection of methods for Segment Routing.
 */
public class SegmentRouting {

	/** Whether working in debug mode */
	protected static boolean DEBUG=false;

	
	/** Prints a debug message.
	 * @param str the string to be printed */
	protected static void debug(String str) {
		if (DEBUG) System.out.println("DEBUG: SegmentRouting: "+str);
	}

	
	/** Gets segments.
	 * @param graph the network graph
	 * @param assigned_path the assigned path
	 * @return array of segments identified by the corresponding destination node */
	public static Node[] getSegments(Graph graph, Path assigned_path) throws Exception {
		List<Node> ap_nodes=assigned_path.getNodePath();
		Node dst=ap_nodes.get(ap_nodes.size()-1);	
		ArrayList<Node> segments=new ArrayList<Node>();
		Node segment;
		while (!(segment=getFirstSegment(graph,assigned_path)).equals(dst)) {
			segments.add(segment);
			debug("getSegments(): segment: "+segment);
			assigned_path=subpath(assigned_path,segment);
		}
		// add destination as last segment
		segments.add(dst);
		return segments.toArray(new Node[]{});
	}


	/** Gets first segment.
	 * @param graph the network graph
	 * @param assigned_path the assigned path
	 * @return the node corresponding to the first segment */
	/*static Node getFirstSegment(Graph graph, Path assigned_path) throws Exception {
		debug("getFirstSegment(): assigned_path: "+assigned_path);
		List<Node> ap_nodes=assigned_path.getNodePath();
		Node src=ap_nodes.get(0);
		Node dst=ap_nodes.get(ap_nodes.size()-1);	
		Set<Path> natural_paths=getNaturalPaths(graph,src.getId(),dst.getId());
		
		if (natural_paths.size()==0) throw new Exception("No natural path has been found");
		// else, natural path exists
		if (natural_paths.size()==1) {
			Path natural_path=natural_paths.iterator().next();
			if (same(natural_path,assigned_path)) {
				debug("getFirstSegment(): found");
				return dst;
			}
			// else continue
		}
		// else, the two path differ
		Path sub_path=assigned_path.getACopy();
		sub_path.popNode();
		return getFirstSegment(graph,sub_path);
	}*/

	
	/** Gets first segment.
	 * @param graph the network graph
	 * @param assigned_path the assigned path
	 * @return the node corresponding to the first segment */
	static Node getFirstSegment(Graph graph, Path assigned_path) throws Exception {
		debug("getFirstSegment(): assigned_path: "+assigned_path);
		List<Node> ap_nodes=assigned_path.getNodePath();
		Node src=ap_nodes.get(0);
		Node dst=ap_nodes.get(ap_nodes.size()-1);	
		Iterator<Path> natural_paths=getNaturalPaths(graph,src.getId(),dst.getId()).iterator();
		
		if (!natural_paths.hasNext()) throw new Exception("No natural path has been found");
		// else, natural path exists
		Path first_natural_path=natural_paths.next();
		if (!natural_paths.hasNext()) {
			// only one natural path
			if (same(first_natural_path,assigned_path)) {
				debug("getFirstSegment(): found");
				return dst;
			}
			// else continue
		}
		// else, the two path differ
		Path sub_path=assigned_path.getACopy();
		sub_path.popNode();
		return getFirstSegment(graph,sub_path);
	}


	/** Gets one equal-cost natural path between two nodes.
	 * @param graph the network graph
	 * @param src the source node
	 * @param dst the destination node
	 * @return one equal-cost natural path between the two nodes */
	/*public static Path getNaturalPath(Graph graph, String src, String dst) {
		return getNaturalPaths(graph,src,dst).iterator().next();
	}*/
	
	
	/** Gets one equal-cost natural path between two nodes.
	 * @param graph the network graph
	 * @param src the source node
	 * @param dst the destination node
	 * @return one equal-cost natural path between the two nodes */
	public static Path getNaturalPath(Graph graph, String src, String dst) {
		Iterator<Path> i=getNaturalPaths(graph,src,dst).iterator();
		if (i.hasNext()) return i.next();
		else return null;
	}
	
	
	/** Gets all equal-cost natural paths between two nodes.
	 * @param graph the network graph
	 * @param src the source node
	 * @param dst the destination node
	 * @return array of equal-cost natural paths between the two nodes */
	/*public static Set<Path> getNaturalPaths(Graph graph, String src, String dst) {
		debug("getNaturalPaths(): src="+src+" dst="+dst);
		Node src_node=graph.getNode(src);
		Node dst_node=graph.getNode(dst);
		HashSet<Path> ec_paths=new HashSet<Path>();
		Dijkstra dijstra=new Dijkstra();
		dijstra.init(graph);
		dijstra.setSource(src_node);
		dijstra.compute();
		Path path=dijstra.getPath(dst_node);
		debug("getNaturalPaths(): path: "+path);
		ec_paths.add(path);
		return ec_paths;
	}*/

	
	/** Gets all equal-cost shortest paths between two nodes.
	 * @param graph the network graph
	 * @param src the source node
	 * @param dst the destination node
	 * @return set of equal-cost shortest paths between the two nodes */
	public static Iterable<Path> getNaturalPaths(Graph graph, String src, String dst) {
		debug("getNaturalPaths(): src="+src+" dst="+dst);
		Node src_node=graph.getNode(src);
		Node dst_node=graph.getNode(dst);
		Dijkstra dijstra=new Dijkstra();
		dijstra.init(graph);
		dijstra.setSource(src_node);
		dijstra.compute();
		Iterable<Path> paths=dijstra.getAllPaths(dst_node);
		int count=0;
		for (Path p : paths) debug("getNaturalPaths(): ECSP["+(count++)+"]: "+p);
		return paths;
	}
	
	
	/** Compares two paths.
	 * @param p1 the first path
	 * @param p2 the second path
	 * @return <i>true</i> if the two paths are equal */
	static boolean same(Path p1, Path p2) {
		//return p1.equals(p2);
		if (p1.size()!=p2.size()) return false;
		// else
		Iterator<Edge> p1_i=p1.getEdgeIterator();
		Iterator<Edge> p2_i=p2.getEdgeIterator();
		while (p1_i.hasNext()) if (!p1_i.next().getId().equals(p2_i.next().getId())) return false;
		// else
		return true;
	}


	/** Return a sub-path.
	 * @param path the original path
	 * @param src the source node
	 * @return the sub-path starting from the given node */
	static Path subpath(Path path, Node src) {
		return subpath(path,src,null);
	}


	/** Return a sub-path.
	 * @param path the original path
	 * @param src the source node
	 * @param dst the destination node
	 * @return the sub-path between the two nodes */
	static Path subpath(Path path, Node src, Node dst) {
		List<Edge> edges=path.getEdgePath();
		Iterator<Node> nodes=path.getNodePath().iterator();
		Path sub_path=null;
		for (Edge edge : edges) {
			Node node_i=nodes.next();
			if (sub_path==null) {
				if (src.equals(node_i)) {
					sub_path=new Path();
					sub_path.setRoot(src);
					sub_path.add(edge);
				}
			}
			else {
				sub_path.add(edge);
				if (dst!=null && dst.equals(edge.getTargetNode())) break;
			}	
		}
		return sub_path;
	}	

}
