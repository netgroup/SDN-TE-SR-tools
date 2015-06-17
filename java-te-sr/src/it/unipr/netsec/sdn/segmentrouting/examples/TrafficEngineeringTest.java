package it.unipr.netsec.sdn.segmentrouting.examples;



import it.unipr.netsec.sdn.segmentrouting.SegmentRouting;
import it.unipr.netsec.sdn.segmentrouting.TrafficEngineering;
import it.unipr.netsec.sdn.segmentrouting.TrafficFlow;

import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.Path;

import java.util.Arrays;



/** Traffic Engineering test.
 */
public class TrafficEngineeringTest {

	
	/** No constructor is available. */
	public TrafficEngineeringTest() {
	}
	
		
	/** Prints a message.
	 * @param str the string to be logged */
	protected static void println(String str) {
		System.out.println(str);
	}


	/** Adds a new traffic flow computing the assigned path and SR identifiers.
	 * @param te network with traffic engineering
	 * @param src the source node
	 * @param dst the destination node
	 * @param bandwidth the flow bandwidth
	 * @return <i>true</i> if it succeeded in both path and SR assignments
	 * @throws Exception */
	public static boolean addFlowSR(TrafficEngineering te, String src, String dst, double bandwidth) throws Exception {
		TrafficFlow flow=new TrafficFlow(src,dst,bandwidth);
		println("Add flow: "+flow);
		println("Natural path: "+SegmentRouting.getNaturalPath(te.getOriginalNetwork(),src,dst));
		boolean success=te.addFlow(flow);
		if (success) {
			Path path=te.getAllocatedPath(flow);
			println("Assigned path: "+path);
			println("Network: "+te.toString());
			Node[] segments=SegmentRouting.getSegments(te.getOriginalNetwork(),path);
			println("SR: "+Arrays.toString(segments));
			return true;
		}
		else {
			println("Failure");
			return false;
		}
	}

	
	/** Main method. */
	public static void main(String[] args) {
		//Graph network=NetworkGraphFactory.getTestNetworkGraph_1("NetworkGraph 1");
		//String src="G";
		//String dst="H";
		Graph network=NetworkGraphFactory.getTestNetworkGraph_2("NetworkGraph 2");
		String src="A";
		String dst="E";
		double bandwidth=1;
		
		//TrafficEngineering.DEBUG=true;
		TrafficEngineering te=new TrafficEngineering(network);
		println("Network: "+te);
		
		try {
			int count=0;
			do {
				println("\nAdd flow #"+(++count));
			}
			while (addFlowSR(te,src,dst,bandwidth));
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}

}
