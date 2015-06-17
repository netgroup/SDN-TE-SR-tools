package it.unipr.netsec.sdn.trafficflow.element;

import com.google.gson.Gson;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

public class FlowCatalogueElement {
	
	private String src;
	private String dst;
	private FlowCatalogueElementFeatures features;
	
	public FlowCatalogueElement(String nodeSrc, String nodeDst, FlowCatalogueElementFeatures nodeFeatures) {
		this.src = nodeSrc;
		this.dst = nodeDst;
		this.features = nodeFeatures;
	}

	public String getSrc() { return this.src; }
	public void setSrc(String nodeSrc) { this.src = nodeSrc; }
	
	public String getDst() { return this.dst; }
	public void setDst(String nodeDst) { this.dst = nodeDst; }

	public FlowCatalogueElementFeatures getFeatures() { return this.features; }
	public void setFeatures(FlowCatalogueElementFeatures nodeFeatures) { this.features = nodeFeatures; }
	
	@Override
	public String toString() {
		StringBuffer sb = new StringBuffer();
		//sb.append("[");
		sb.append("\"" + this.src + "\",");
		sb.append("\"" + this.dst + "\",");
		sb.append(new Gson().toJson(this.features));
		//sb.append("]");
		
		return sb.toString();
	}
	
}
