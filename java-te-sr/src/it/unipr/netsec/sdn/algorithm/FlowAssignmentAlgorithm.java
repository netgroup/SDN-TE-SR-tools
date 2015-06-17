package it.unipr.netsec.sdn.algorithm;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;

import it.unipr.netsec.sdn.graph.util.GraphConstant;
import it.unipr.netsec.sdn.trafficflow.element.FlowElement;
import it.unipr.netsec.sdn.trafficflow.element.TrafficFlowContainer;

import org.graphstream.algorithm.Dijkstra;
import org.graphstream.algorithm.DynamicAlgorithm;
import org.graphstream.graph.Edge;
import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.Path;
import org.graphstream.graph.implementations.MultiGraph;
import org.graphstream.stream.SinkAdapter;

/**
 * Traffic Flow Assignment algorithm implementation
 */
public class FlowAssignmentAlgorithm extends SinkAdapter implements DynamicAlgorithm {
	
	private boolean terminate = false;
	
	private Graph g = null;
	private Graph inner = null;
	
	private TrafficFlowContainer flows = null;
	private TrafficFlowContainer partialFlows = null;
	
	private double sigma = 0.0;
	private double Tglob = 0.0;
	private double Tfin = 0.0;
	
	private boolean directedEdge = true;
	
	@Override
	public void init(Graph graph) {
		g = graphCopy(graph, graph.getId() + "_INIT");
		g.addSink(this);
		
		partialFlows = new TrafficFlowContainer();
	}

	@Override
	public void compute() {
		initialFlowAllocation();

		Tglob = averageDelayCalculation(inner);
		
		finalTimeAllocation(Tglob);
		
		boolean iterate = true;
		/*
		while (iterate) {
			for (int ii = 0; ii < flows.size(); ii++) {				
				flowAllocationLoop(flows.get(ii));
			}
			
			iterate = timesComparison();
		}
		*/
		while (iterate) {
			for (int ii = 0; ii < partialFlows.size(); ii++) {				
				flowAllocationLoop(partialFlows.get(ii));
			}
			
			iterate = timesComparison();
		}
	}

	@Override
	public void terminate() {
		g.removeSink(this);
		terminate = true;
	}
	
	/** Set the traffic flows container
	 * 	@param tfc the traffic flows container
	 */
	public void setTrafficFlows(TrafficFlowContainer tfc) {
		flows = tfc;
	}
	
	/** Return a container of traffic flows, enhanced with allocated paths
	 * 	@return the allocated paths
	 */
	public TrafficFlowContainer getFlowAssignment() {
		if (terminate) {
			//return flows;
			return partialFlows;
		}
		
		return null;
	}
	
	/** Return the updated network
	 * 	@return the updated network
	 */
	public Graph getUpdatedGraph() {
		return graphCopy(inner, inner.getId() + "_COPY");
	}
	
	public void setDirectedEdge(boolean directed) { this.directedEdge = directed; }
	public boolean isDirectedEdge() { return this.directedEdge; }
	
	/** Step 2:
	 * 	First FLOW ALLOCATION
	 */
	private void initialFlowAllocation() {
		inner = graphCopy(g, g.getId() + "_INNER");
		
		double BIGK = 0.0;
		
		for (Edge e : inner.getEdgeSet()) {
			double nominalCapacity = e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_CAPACITY);
			if (nominalCapacity > BIGK) {
				BIGK = nominalCapacity;
			}
		}
		
		HashMap<String, TrafficFlowContainer> edgesUtilization = new HashMap<String, TrafficFlowContainer>();
		for (Edge e : inner.getEdgeSet()) {
			String key = "(" + e.getSourceNode().getId() + "," + e.getTargetNode().getId() + ")";
			edgesUtilization.put(key, new TrafficFlowContainer());
		}
		
		for (FlowElement f : flows) {
			Graph innerTMP = new MultiGraph("TMPGraph");
			for (Node node : inner.getNodeSet()) {
				Node n = innerTMP.addNode(node.getId());
				for (String attribute : node.getAttributeKeySet()) {
					n.addAttribute(attribute, node.getAttribute(attribute));
				}
			}
			
			for (Edge e : inner.getEdgeSet()) {
				double nominalCapacity = e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_CAPACITY);
				double load = e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
				double residualCapacity = nominalCapacity - load;
				
				double linkCost = BIGK / residualCapacity;
				
				e.addAttribute(GraphConstant.ATTRIBUTE_EDGE_COST, linkCost);
				
				// If there is enough capacity, we add this edge to a temporary graph
				double flowBW = f.getBandwidth();
				if ((residualCapacity - flowBW) >= 0.0) {
					Edge eTmp = innerTMP.addEdge(e.getId(), e.getSourceNode().getId(), e.getTargetNode().getId(), this.directedEdge);
					for (String attribute : e.getAttributeKeySet()) {
						eTmp.addAttribute(attribute, e.getAttribute(attribute));
					}
				}
			}
			
			Node source = innerTMP.getNode(f.getNodeSource());
			
			Dijkstra d = new Dijkstra(Dijkstra.Element.EDGE, "result", GraphConstant.ATTRIBUTE_EDGE_COST);
			d.init(innerTMP);
			d.setSource(source);
			d.compute();
				
			Node dest = innerTMP.getNode(f.getNodeDestination());
			
			String path = "";
			for (Edge pathEdge : d.getPathEdges(dest)) {
				double load = inner.getEdge(pathEdge.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
				load += f.getBandwidth();
				inner.getEdge(pathEdge.getId()).addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, load);
				String key = "(" + pathEdge.getSourceNode().getId() + "," + pathEdge.getTargetNode().getId() + ")";
				path = "," + key + path;
				edgesUtilization.get(key).add(f);
			}
			
			f.setPath(d.getPath(dest));
			
			if (f.getPath().size() > 0) {
				partialFlows.add(f);
			}
			
			innerTMP.clearSinks();
			innerTMP.clearElementSinks();
			innerTMP.clearAttributeSinks();
			innerTMP.clearAttributes();
			innerTMP.clear();
		}
		
		for (Edge e : g.getEdgeSet()) {
			String key = "(" + e.getSourceNode().getId() + "," + e.getTargetNode().getId() + ")";
			if (edgesUtilization.get(key) != null) {
				double count = 0;
				for (FlowElement fe : edgesUtilization.get(key)) {
					count += fe.getBandwidth();
				}
				e.addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, count);
			}
		}
	}
	
	/** Step 3:
	 * 	Delay calculation on provided graph, as T_glob
	 * 	@param graph Graph on which calculate average delay, as T_glob
	 * 	@return T_glob = average delay
	 */
	private double averageDelayCalculation(Graph graph) {
		sigma = 0.0;
		
		/*
		for (FlowElement f : flows) {
			sigma += f.getBandwidth();
		}
		*/
		for (FlowElement f : partialFlows) {
			sigma += f.getBandwidth();
		}
		
		double localTglob = 0.0;
		for (Edge e : graph.getEdgeSet()) {
			double capacity = e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_CAPACITY);
			double load = e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
			localTglob +=  load / (capacity - load);
		}
		
		localTglob = (1 / sigma) * localTglob;
		
		return localTglob;
	}
	
	/** Step 4:
	 * 	Assign to Tfin a T_glob value
	 * 	@param glob the T_glob value that has to be assigned to T_final
	 */
	private void finalTimeAllocation(double glob) {
		Tfin = glob;
	}
	
	/** Steps 5-6-7:
	 * 	Flow allocation loop, to test if exists others available allocations for the provided flows.
	 * 	@param cfe Flow element that has to be eventually re-allocated, exploiting the algorithm
	 */
	private void flowAllocationLoop(FlowElement cfe) {
		Graph tmp = graphCopy(inner, inner.getId() + "_STEP567");
		
		// Deallocate current flow from temporary graph
		for (Edge e : cfe.getPath().getEdgeSet()) {
			double load = tmp.getEdge(e.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
			load = load - cfe.getBandwidth();
			tmp.getEdge(e.getId()).addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, load);
		}
		
		// Prune edges that doesn't support the current flow
		ArrayList<Edge> pruned = new ArrayList<Edge>();
		for (Edge e : tmp.getEdgeSet()) {
			double capacity = e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_CAPACITY);
			double load = e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
			load += cfe.getBandwidth();
			if (capacity <= load) {
				pruned.add(e);
				tmp.removeEdge(e);
			}
		}
		
		// Edge length calculation, with the UniRoma2 formula
		for (Edge e : tmp.getEdgeSet()) {
			double capacity = e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_CAPACITY);
			double load = e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
			double length = capacity / (Math.pow(capacity - load, 2));
			length = (1 / sigma) * length;
			e.addAttribute(GraphConstant.ATTRIBUTE_EDGE_LENGTH, length);
		}
		
		Node source = tmp.getNode(cfe.getNodeSource());
		
		// CSPF --> Dijkstra
		Dijkstra d = new Dijkstra(Dijkstra.Element.EDGE, "result", GraphConstant.ATTRIBUTE_EDGE_LENGTH);
		d.init(tmp);
		d.setSource(source);
		d.compute();
		
		Node dest = tmp.getNode(cfe.getNodeDestination());
		
		int count = 0;
		for (Path p : d.getAllPaths(dest)) {
			count++;
		}
		
		Path path = cfe.getPath();
		double pathLength = 0.0;
		for (Edge e : path.getEdgeSet()) {
			pathLength += (double) tmp.getEdge(e.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LENGTH);
		}
		
		if (count > 1) {
			for (Path p : d.getAllPaths(dest)) {
				double pl = 0.0;
				for (Edge e : p.getEdgeSet()) {
					pl += (double) tmp.getEdge(e.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LENGTH);
				}
				
				if ((pl < pathLength) && (!pathEquals(p, path))) {
					path = p;
					pathLength = pl;					
				}
			}
			
			// Sum discovered path to temporary graph
			for (Edge e : path.getEdgeSet()) {
				double load = tmp.getEdge(e.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
				load += cfe.getBandwidth();
				tmp.getEdge(e.getId()).addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, load);
			}
			
			// BEFORE re-calculate the delay time, re-add previously pruned edges to temporary graph
			for (Edge e : pruned) {
				Edge ne = tmp.addEdge(e.getId(), e.getSourceNode(), e.getTargetNode(), this.directedEdge);
				for (String keyAttribute : e.getAttributeKeySet()) {
					ne.addAttribute(keyAttribute, e.getAttribute(keyAttribute));
				}
			}
			
			double localTglob = averageDelayCalculation(tmp);
			if (localTglob < Tfin) {
				finalTimeAllocation(localTglob);
				
				// Delete OLD path for the current flow from the graph
				for (Edge e : cfe.getPath().getEdgeSet()) {
					double load = inner.getEdge(e.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
					load -= cfe.getBandwidth();
					inner.getEdge(e.getId()).addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, load);
				}
				
				// Add NEW path for the current flow to the graph
				for (Edge e : path.getEdgeSet()) {
					double load = inner.getEdge(e.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
					load += cfe.getBandwidth();
					inner.getEdge(e.getId()).addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, load);
				}
				
				// Add NEW path to the current flow
				cfe.setPath(path);
			}
		}
		else {
			Path found = d.getPath(dest);
			double dijkstraPathLength = 0.0;
			for (Edge e : found.getEdgeSet()) {
				dijkstraPathLength += (double) e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_LENGTH);
			}
			
			if (dijkstraPathLength < pathLength) {				
				// Sum discovered path to temporary graph
				for (Edge e : found.getEdgeSet()) {
					double load = tmp.getEdge(e.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
					load += cfe.getBandwidth();
					tmp.getEdge(e.getId()).addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, load);
				}
				
				// BEFORE re-calculate the delay time, re-add previously pruned edges to temporary graph
				for (Edge e : pruned) {
					Edge ne = tmp.addEdge(e.getId(), e.getSourceNode(), e.getTargetNode(), this.directedEdge);
					for (String keyAttribute : e.getAttributeKeySet()) {
						ne.addAttribute(keyAttribute, e.getAttribute(keyAttribute));
					}
				}
				
				double localTglob = averageDelayCalculation(tmp);
				if (localTglob < Tfin) {
					finalTimeAllocation(localTglob);
					
					// Delete OLD path for the current flow from the graph
					for (Edge e : path.getEdgeSet()) {
						double load = inner.getEdge(e.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
						load -= cfe.getBandwidth();
						inner.getEdge(e.getId()).addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, load);
					}
					
					// Add NEW path for the current flow to the graph
					for (Edge e : found.getEdgeSet()) {
						double load = inner.getEdge(e.getId()).getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD);
						load += cfe.getBandwidth();
						inner.getEdge(e.getId()).addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, load);
					}
					
					// Add NEW path to the current flow
					cfe.setPath(found);
					path = found;
					pathLength = dijkstraPathLength;
				}
			}
		}
	}
	
	/** Step 8:
	 * 	Comparison between actual T_fin time and T_glob time.
	 * 	@return TRUE if t_fin is lower than T_glob, FALSE otherwise.
	 */
	private boolean timesComparison() {
		if (Tfin < Tglob) {
			Tglob = Tfin;
			return true;
		}
		else if (Tfin == Tglob) {
			return false;
		}
		
		return true;
	}
	
	private static boolean pathEquals(Path p1, Path p2) {
		if (p1.size() != p2.size()) {
			return false;
		}
		
		Iterator<Edge> p1_i = p1.getEdgeIterator();
		Iterator<Edge> p2_i = p2.getEdgeIterator();
		while (p1_i.hasNext()) {
			if (!p1_i.next().getId().equals(p2_i.next().getId())) {
				return false;
			}
		}
		
		return true;
	}
	
	private Graph graphCopy(Graph graph, String name) {
		Graph cpy = new MultiGraph(name);
		
		for (Node node : graph.getNodeSet()) {
			Node n = cpy.addNode(node.getId());
			for (String attribute : node.getAttributeKeySet()) {
				n.addAttribute(attribute, node.getAttribute(attribute));
			}
		}
		
		for (Edge edge : graph.getEdgeSet()) {
			Edge e = cpy.addEdge(edge.getId(), edge.getSourceNode().getId(), edge.getTargetNode().getId(), this.directedEdge);
			for (String attribute : edge.getAttributeKeySet()) {
				e.addAttribute(attribute, edge.getAttribute(attribute));
			}
		}
		
		return cpy;
	}

}
