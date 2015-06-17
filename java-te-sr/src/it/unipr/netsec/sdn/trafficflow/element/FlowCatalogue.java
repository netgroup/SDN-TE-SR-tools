package it.unipr.netsec.sdn.trafficflow.element;

import java.util.HashMap;
import java.util.Map;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

public class FlowCatalogue extends HashMap<String, FlowCatalogueElement> {

	private static final long serialVersionUID = -6071289729851475943L;
	
	@Override
	public String toString() {
		StringBuilder sb = new StringBuilder();
		sb.append("{");
		
		for (Map.Entry<String, FlowCatalogueElement> entry : this.entrySet()) {
			sb.append("\"" + entry.getKey() + "\":");
			sb.append("[");
			sb.append(entry.getValue().toString());
			sb.append("]");
			sb.append(",");
		}
		sb.deleteCharAt(sb.length() - 1);
		
		sb.append("}");
		return sb.toString();
	}

}
