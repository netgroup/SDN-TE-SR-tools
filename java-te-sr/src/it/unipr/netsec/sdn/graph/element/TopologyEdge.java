package it.unipr.netsec.sdn.graph.element;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/


/**
 * Represent a topology edge
 */
public class TopologyEdge {
	private String v1;
	private String v2;
	private String label;
	private String type;
	private double capacity;
	private double load;
	
	public TopologyEdge() {
		this.v1 = "";
		this.v2 = "";
		this.label = "";
		this.type = "";
		this.capacity = 1;
		this.load = 0;
	}
	
	public TopologyEdge(String vertex1, String vertex2, String edgeLabel, String edgeType) {
		this.v1 = vertex1;
		this.v2 = vertex2;
		this.label = edgeLabel;
		this.type = edgeType;
		this.capacity = 1;
		this.load = 0;
	}
	
	public TopologyEdge(String vertex1, String vertex2, String edgeLabel, String edgeType, double edgeCapacity, double edgeLoad) {
		this(vertex1, vertex2, edgeLabel, edgeType);
		this.capacity = edgeCapacity;
		this.load = edgeLoad;
	}
	
	public String getV1() { return this.v1; }
	public void setV1(String vertex1) { this.v1 = vertex1; }
	
	public String getV2() { return this.v2; }
	public void setV2(String vertex2) { this.v2 = vertex2; }
	
	public String getLabel() { return this.label; }
	public void setLabel(String edgeLabel) { this.label = edgeLabel; }
	
	public String getType() { return this.type; }
	public void setType(String edgeType) { this.type = edgeType; }

	public double getCapacity() { return capacity; }
	public void setCapacity(double edgeCapacity) { this.capacity = edgeCapacity; }

	public double getLoad() { return load; }
	public void setLoad(double edgeLoad) { this.load = edgeLoad; }
	
}
