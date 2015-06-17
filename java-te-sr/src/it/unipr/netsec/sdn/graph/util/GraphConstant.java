package it.unipr.netsec.sdn.graph.util;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

/**
 * Network graph constants
 */
public interface GraphConstant {
	
	public static final String CORE_ROUTER = "OSHICR";
	public static final String PROVIDER_EDGE_ROUTER = "OSHIPE";
	public static final String CUSTOMER_EDGE_ROUTER = "CE";
	
	public static final String ATTRIBUTE_NODE_TYPE = "node_type";
	
	public static final String ATTRIBUTE_EDGE_LABEL = "edge_label";
	public static final String ATTRIBUTE_EDGE_TYPE = "edge_type";
	public static final String ATTRIBUTE_EDGE_CAPACITY = "edge_capacity";
	public static final String ATTRIBUTE_EDGE_LOAD = "edge_load";
	public static final String ATTRIBUTE_EDGE_COST = "edge_cost";
	public static final String ATTRIBUTE_EDGE_LENGTH = "edge_length";

}
