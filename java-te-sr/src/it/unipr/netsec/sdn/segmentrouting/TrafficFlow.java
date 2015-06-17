package it.unipr.netsec.sdn.segmentrouting;




/** A traffic flow is characterized by a source node, a destination node, and bandwidth.
 */
public class TrafficFlow {

	/** Source node */
	String src;

	/** Destination node */
	String dst;

	/** Bandwidth */
	double bandwidth;

	
	/** Creates a new traffic flow. 
	 * @param src the source node
	 * @param dst the destination node
	 * @param bandwidth the flow bandwidth */
	public TrafficFlow(String src, String dst, double bandwidth) {
		this.src=src;
		this.dst=dst;
		this.bandwidth=bandwidth;
	}
	
	/**Gets the source node.
	 * @return the source node */
	public String getSource() {
		return src;
	}

	/** Gets the destination node.
	 * @return the destination node */
	public String getDestination() {
		return dst;
	}

	/** Gets the flow bandwidth.
	 * @return the bandwidth */
	public double getBandwidth() {
		return bandwidth;
	}
	
	@Override
	public String toString() {
		return "[src="+src+",dst="+dst+",bwd="+bandwidth+"]";
	}
	
}
