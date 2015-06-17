package it.unipr.netsec.sdn.segmentrouting;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import it.unipr.netsec.sdn.trafficflow.element.FlowElement;

import java.util.HashMap;
import java.util.Set;

import org.graphstream.graph.Node;
import org.graphstream.graph.Path;

public class SegmentRoutingCatalogue {
	
	private HashMap<FlowElement, SegmentRoutingCatalogueElement> catalogue = null;

	public SegmentRoutingCatalogue() {
		catalogue = new HashMap<>();
	}
	
	public Set<FlowElement> getFlowElements() { return this.catalogue.keySet();	}
	
	public void addSegmentRoutingElement(FlowElement flow, Path naturalPath, Node[] segments) {
		this.catalogue.put(flow, new SegmentRoutingCatalogueElement(naturalPath, segments));
	}
	
	public Path getAssignedPath(String flowID) {
		for (FlowElement f : this.catalogue.keySet()) {
			if (f.getId().equals(flowID)) {
				return f.getPath();
			}
		}
		
		return null;
	}
	
	public Path getNaturalPath(String flowID) {
		for (FlowElement f : this.catalogue.keySet()) {
			if (f.getId().equals(flowID)) {
				return this.catalogue.get(f).getNaturalPath();
			}
		}
		
		return null;
	}
	
	public Node[] getSegments(String flowID) {
		for (FlowElement f : this.catalogue.keySet()) {
			if (f.getId().equals(flowID)) {
				return this.catalogue.get(f).getSegments();
			}
		}
		
		return null;
	}
	
	
	private class SegmentRoutingCatalogueElement {
		private Path naturalPath;
		private Node[] segments;
	
		public SegmentRoutingCatalogueElement(Path naturalPath, Node[] segments) {
			this.naturalPath = naturalPath;
			this.segments = segments;
		}
		
		public Path getNaturalPath() { return this.naturalPath; }
		public Node[] getSegments() { return this.segments; }
	}
}
