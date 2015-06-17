package it.unipr.netsec.sdn.graph.element;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import com.google.gson.annotations.SerializedName;

public class TopologyCatalogueElementFeatures {

    private double allocated;
    private double capacity;
    @SerializedName("dst_mac") private String dstMAC;
	@SerializedName("dst_port") private String dstPort;
	@SerializedName("ds_port_no") private String dstPortNo;
	private String[] flows;
	private String id = null;
	@SerializedName("src_mac") private String srcMAC;
	@SerializedName("src_port") private String srcPort;
	@SerializedName("src_port_no") private String srcPortNo;

    public String getSrcPortNo() { return this.srcPortNo; }
    public void setSrcPortNo(String srcPortNo) { this.srcPortNo = srcPortNo; }

    public String getDstMAC() { return this.dstMAC; }
    public void setDstMAC(String dstMAC) { this.dstMAC = dstMAC; }

    public String getDstPort() { return this.dstPort; }
    public void setDstPort(String dstPort) { this.dstPort = dstPort; }

    public String getDstPortNo() { return this.dstPortNo; }
    public void setDstPortNo(String dstPortNo) { this.dstPortNo = dstPortNo; }

    public String getSrcMAC() { return this.srcMAC; }
    public void setSrcMAC(String srcMAC) { this.srcMAC = srcMAC; }

    public double getCapacity() { return this.capacity; }
    public void setCapacity(double capacity) { this.capacity = capacity; }

    public double getAllocated() { return this.allocated; }
    public void setAllocated(double allocated) { this.allocated = allocated; }

    public String getSrcPort() { return this.srcPort; }
    public void setSrcPort(String srcPort) { this.srcPort = srcPort; }

    public String[] getFlows() { return this.flows; }
    public void setFlows(String[] flows) { this.flows = flows; }
    
    public String getId() { return this.id; }
    public void setId(String id) { this.id = id; }
    
}