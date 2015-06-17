package it.unipr.netsec.sdn.run;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import java.util.Arrays;

import org.graphstream.graph.Edge;
import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.Path;

import it.unipr.netsec.sdn.algorithm.FlowAssignmentAlgorithm;
import it.unipr.netsec.sdn.benchmark.BenchmarkFactory;
import it.unipr.netsec.sdn.graph.GraphFactory;
import it.unipr.netsec.sdn.segmentrouting.SegmentRouting;
import it.unipr.netsec.sdn.segmentrouting.SegmentRoutingCatalogue;
import it.unipr.netsec.sdn.trafficflow.TrafficFlowFactory;
import it.unipr.netsec.sdn.trafficflow.element.FlowElement;
import it.unipr.netsec.sdn.trafficflow.element.TrafficFlowContainer;
import it.unipr.netsec.sdn.util.CMDParams;
import it.unipr.netsec.sdn.util.Utils;

public class Main {
	
	public static void main(String[] args) {
		CMDParams params = Utils.parseCMD(args);
		String topo = params.get(Utils.CMDPARAMS_TOPO_IN);
		String outTopo = params.get(Utils.CMDPARAMS_TOPO_OUT);
		
		String flows = params.get(Utils.CMDPARAMS_FLOWS_IN);
		String outFlows = params.get(Utils.CMDPARAMS_FLOWS_OUT);
		
		boolean DEBUG = Boolean.parseBoolean(params.get(Utils.CMDPARAMS_DEBUG));
		
	//Graph Builder
		GraphFactory gf = new GraphFactory();
		gf.loadTopologyCatalogueFromJSONFile(topo);
		gf.buildGraphStreamTopology();
		//GraphFactory.displayPoorGraph(gf.getGraph(), false);
		
	//Traffic Flow Generator
		TrafficFlowFactory tff = new TrafficFlowFactory();
		tff.loadFlowCatalogueFromJSONFile(flows);
		if (DEBUG) {
			System.out.println("Flows #: " + tff.getTrafficFlows().size());
		}
		
		long deltaFlowAssignment;
		long deltaSegmentRouting;
	
	// Flow Assignment Algorithm
		FlowAssignmentAlgorithm faa = new FlowAssignmentAlgorithm();
		faa.init(gf.getGraph());
		faa.setTrafficFlows(tff.getTrafficFlows());
		deltaFlowAssignment = System.currentTimeMillis();
		faa.compute();
		deltaFlowAssignment = System.currentTimeMillis() - deltaFlowAssignment;
		faa.terminate();
		
		Graph finalGraph = faa.getUpdatedGraph();
		TrafficFlowContainer finalTrafficFlowAssignment = faa.getFlowAssignment();
		
		//GraphFactory.displayGraphWithFlows(finalGraph, finalTrafficFlowAssignment, false);
		if (DEBUG) {
			System.out.println();
			System.out.println("FLOW ALLOCATION");
			System.out.println("\tID\tFlow\t\tPath");
			for (FlowElement fe : finalTrafficFlowAssignment) {
				System.out.print("\t" + fe.getId());
				System.out.print("\t(" + fe.getNodeSource() + "," + fe.getNodeDestination() + ")");
				System.out.print("\t\t");
				String path = "";
				for (Edge e : fe.getPath().getEdgeSet()) {
					path += "(" + e.getSourceNode() + "," + e.getTargetNode() + "),";				
				}
				if (path.length() > 0) {
					System.out.print(path.substring(0, path.length() - 1));
				}
				else {
					System.out.println("NO PATH!");
				}
				System.out.println();
			}
			System.out.println();
		}
		
	// Segment Routing Algorithm
		if (DEBUG) {
			System.out.println();
			System.out.println("SEGMENT ROUTING ALLOCATION");
		}
		
		SegmentRoutingCatalogue srCatalogue = new SegmentRoutingCatalogue();
		deltaSegmentRouting = System.currentTimeMillis();
		for (FlowElement fe : finalTrafficFlowAssignment) {
			Path assignedPath = fe.getPath();
			Path naturalPath = SegmentRouting.getNaturalPath(gf.getGraph(), fe.getNodeSource(), fe.getNodeDestination());
			try {
				Node[] segments = SegmentRouting.getSegments(gf.getGraph(), assignedPath);
				srCatalogue.addSegmentRoutingElement(fe, naturalPath, segments);
				tff.addSegmentsToTrafficFlow(fe, segments);
			}
			catch (Exception e) {
				e.printStackTrace();
				srCatalogue.addSegmentRoutingElement(fe, naturalPath, new Node[0]);
				tff.addSegmentsToTrafficFlow(fe, new Node[0]);
			}
		}
		deltaSegmentRouting = System.currentTimeMillis() - deltaSegmentRouting;
		
		if (DEBUG) {
			int countFlows = 0;
			for (FlowElement fe : srCatalogue.getFlowElements()) {
				System.out.println("\tFlow: (" + fe.getNodeSource() + "," + fe.getNodeDestination() + "): " + fe.getId());
				
				Path assignedPath = srCatalogue.getAssignedPath(fe.getId());
				Path naturalPath = srCatalogue.getNaturalPath(fe.getId());
				
				System.out.println("\t\tAssigned path:\t" + assignedPath + " --> Len = " + assignedPath.size());
				System.out.println("\t\tNatural path:\t" + naturalPath + " --> Len = " + naturalPath.size());
				
				try {
					Node[] segments = srCatalogue.getSegments(fe.getId());
					System.out.println("\t\tSegments:\t" + Arrays.toString(segments) + " --> Len = " + segments.length);
				}
				catch (Exception e) {
					System.err.println(e.getMessage());
				}
				System.out.println();
				countFlows ++;
			}
			System.out.println("Flows #: " + countFlows);
		}
		
	// Write topology on JSON file (new version)
		gf.saveTopologyToTopologyCatalogue(finalGraph, srCatalogue, outTopo);
		
	// Write traffic flow on JSON file (new version)
		tff.saveTrafficFlowToFlowCatalogue(srCatalogue, outFlows);
		
		if (DEBUG) {
			System.out.println("FlowAssignment Time: " + deltaFlowAssignment + "ms");
			System.out.println("SegmentRouting Time: " + deltaSegmentRouting + "ms");
			
			BenchmarkFactory.histogram(srCatalogue, Integer.toString(gf.getGraph().getNodeCount()), Integer.toString(tff.getTrafficFlows().size()));
			BenchmarkFactory.average(srCatalogue);
		}
	}

}
