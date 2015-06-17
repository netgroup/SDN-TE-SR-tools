package it.unipr.netsec.sdn.segmentrouting.examples;



import it.unipr.netsec.sdn.segmentrouting.*;

import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.Path;

import java.util.Arrays;



/** Segment Routing test.
 */
public class SegmentRoutingTest {

	
	/** No constructor is available. */
	public SegmentRoutingTest() {
	}
	
		
	/** Main method. */
	public static void main(String[] args) {

		Graph graph=NetworkGraphFactory.getTestNetworkGraph_1("TestNetworkGraph 1"); 
		//String[] path_edges={"GA","AD","DE","EC","CF","FH"};
		String[] path_edges={"GA","AB","BC","CF","FH"};
		//String[] path_edges={"GA","AD","DE","EF","FH"};
		Path assigned_path=NetworkGraph.getPath(graph,path_edges);
		System.out.println("assigned path: "+assigned_path);
		System.out.println("natural path: "+SegmentRouting.getNaturalPath(graph,"G","H"));
		
		try {
			Node[] segments=SegmentRouting.getSegments(graph,assigned_path);
			System.out.println("segments: "+Arrays.toString(segments));
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}

}
