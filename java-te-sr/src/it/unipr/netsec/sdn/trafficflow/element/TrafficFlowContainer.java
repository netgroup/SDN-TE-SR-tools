package it.unipr.netsec.sdn.trafficflow.element;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import java.util.ArrayList;

/**
 * Traffic flow container
 */
public class TrafficFlowContainer extends ArrayList<FlowElement> {

	private static final long serialVersionUID = 6012483084184795207L;
	
	public TrafficFlowContainer() {}
	
	public TrafficFlowContainer(ArrayList<FlowElement> a) {
		addAll(a);
	}

}
