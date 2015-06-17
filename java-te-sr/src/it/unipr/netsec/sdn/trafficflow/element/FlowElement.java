package it.unipr.netsec.sdn.trafficflow.element;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import org.graphstream.graph.Edge;
import org.graphstream.graph.Path;

/**
 * Represent a single element of network traffic
 */
public class FlowElement {
	public static final String OUT = "out";
	public static final String IN = "in";
	
	private String id;
	private String nodeSource;
	private String nodeDestination;
	private double bandwidth;
	private Path path = null;
	private String relationID;
	private String relationType;
	
	public FlowElement() {
		this.id = "";
		this.nodeSource = "";
		this.nodeDestination = "";
		this.bandwidth = 0.0;
		this.relationID = "";
		this.relationType = "";
	}
	
	public FlowElement(String flowID, String nodeSrc, String nodeDest, double bandwidth) {
		this.id = flowID;
		this.nodeSource = nodeSrc;
		this.nodeDestination = nodeDest;
		this.bandwidth = bandwidth;
		this.relationID = "";
		this.relationType = "";
	}
	
	public FlowElement(String flowID, String nodeSrc, String nodeDest, double bandwidth, Path p) {
		this(flowID, nodeSrc, nodeDest, bandwidth);
		this.path = p;
	}

	public String getId() { return this.id; }
	public void setId(String flowID) { this.id = flowID; }

	public String getNodeSource() { return this.nodeSource; }
	public void setNodeSource(String nodeSrc) { this.nodeSource = nodeSrc; }

	public String getNodeDestination() { return this.nodeDestination; }
	public void setNodeDestination(String nodeDest) { this.nodeDestination = nodeDest; }

	public double getBandwidth() { return this.bandwidth; }
	public void setBandwidth(double bandwidth) { this.bandwidth = bandwidth; }
	
	public Path getPath() { return this.path; }
	public void setPath(Path p) { this.path = p; }

	public String getRelationID() { return this.relationID; }
	public void setRelationID(String relationID) { this.relationID = relationID; }

	public String getRelationType() { return this.relationType; }
	public void setRelationType(String relationType) { this.relationType = relationType; }

	public void addEdgeToPath(Edge e) { this.path.add(e); }
	
	public String toString() {
		return "ID: " + this.id + ": SRC: " + this.nodeSource + " , DST: " + this.nodeDestination + " , BW: " + this.bandwidth;
	}
	
}
