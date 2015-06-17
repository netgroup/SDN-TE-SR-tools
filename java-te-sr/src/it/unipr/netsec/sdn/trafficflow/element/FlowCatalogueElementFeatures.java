package it.unipr.netsec.sdn.trafficflow.element;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

public class FlowCatalogueElementFeatures {
	
	private FlowCatalogueElementFeaturesDetail in;
	private String id;
	private FlowCatalogueElementFeaturesDetail out;
	
	public FlowCatalogueElementFeaturesDetail getIn() { return this.in; }
	public void setIn(FlowCatalogueElementFeaturesDetail in) { this.in = in; }
	
	public String getId() { return this.id; }
	public void setId(String label) { this.id = label; }
	
	public FlowCatalogueElementFeaturesDetail getOut() { return this.out; }
	public void setOut(FlowCatalogueElementFeaturesDetail out) { this.out = out; }
	
}