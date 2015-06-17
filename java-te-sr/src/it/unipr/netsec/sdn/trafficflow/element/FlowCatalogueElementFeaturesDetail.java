package it.unipr.netsec.sdn.trafficflow.element;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

public class FlowCatalogueElementFeaturesDetail {

	private boolean allocated;
	private String dstPort;
	private String[] path;
    private double size;
    private String srcPort;
    private String type;
    
    public boolean getAllocated() { return this.allocated; }
	public void setAllocated(boolean allocated) { this.allocated = allocated; }
	
	public String getDstPort() { return this.dstPort; }
	public void setDstPort(String dstPort) { this.dstPort = dstPort; }
    
    public String[] getPath() { return this.path; }
    public void setPath(String[] path) { this.path = path; }

    public double getSize() { return this.size; }
    public void setSize(double size) { this.size = size; }
    
    public String getSrcPort() { return this.srcPort; }
	public void setSrcPort(String srcPort) { this.srcPort = srcPort; }
	
	public String getType() { return this.type; }
	public void setType(String type) { this.type = type; }

}
