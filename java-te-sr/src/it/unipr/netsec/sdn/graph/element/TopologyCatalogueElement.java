package it.unipr.netsec.sdn.graph.element;

import com.google.gson.Gson;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

public class TopologyCatalogueElement {
	
	private String src;
	private String dst;
	private TopologyCatalogueElementFeatures features;
	
	public TopologyCatalogueElement(String nodeSrc, String nodeDst, TopologyCatalogueElementFeatures nodeFeatures) {
		this.src = nodeSrc;
		this.dst = nodeDst;
		this.features = nodeFeatures;		
	}

	public String getSrc() { return this.src; }
	public void setSrc(String nodeSrc) { this.src = nodeSrc; }

	public String getDst() { return this.dst; }
	public void setDst(String nodeDst) { this.dst = nodeDst; }

	public TopologyCatalogueElementFeatures getFeatures() { return this.features; }
	public void setFeatures(TopologyCatalogueElementFeatures nodeFeatures) { this.features = nodeFeatures; }
	
	@Override
	public String toString() {
		StringBuffer sb = new StringBuffer();
		sb.append("[");
		sb.append("\"" + this.src + "\",");
		sb.append("\"" + this.dst + "\",");
		sb.append(new Gson().toJson(this.features));
		sb.append("]");
		
		return sb.toString();
	}
}