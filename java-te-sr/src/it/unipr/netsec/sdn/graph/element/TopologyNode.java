package it.unipr.netsec.sdn.graph.element;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

/**
 * Represent a topology node
 */
public class TopologyNode {
	private String label;
	private String type;
	private double x;
	private Double y;
	
	public TopologyNode() {
		this.label = "";
		this.type = "";
		this.x = 0.0;
		this.y = 0.0;
	}
	
	public TopologyNode(String nodeLabel, String nodeType) {
		this.label = nodeLabel;
		this.type = nodeType;
		this.x = 0.0;
		this.y = 0.0;
	}
	
	public String getLabel() { return this.label; }
	public void setLabel(String nodeLabel) { this.label = nodeLabel; }
	
	public String getType() { return this.type; }
	public void setType(String nodeType) { this.type = nodeType; }

	public double getX() { return x; }
	public void setX(double posX) { this.x = posX; }

	public Double getY() { return y; }
	public void setY(Double posY) { this.y = posY; }
	
}