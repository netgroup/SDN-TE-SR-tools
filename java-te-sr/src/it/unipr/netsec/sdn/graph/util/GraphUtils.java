package it.unipr.netsec.sdn.graph.util;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import it.unipr.netsec.sdn.graph.element.TopologyCatalogue;
import it.unipr.netsec.sdn.graph.element.TopologyCatalogueElement;
import it.unipr.netsec.sdn.graph.element.TopologyEdge;
import it.unipr.netsec.sdn.graph.element.TopologyNode;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Random;

import com.google.gson.internal.LinkedTreeMap;

/**
 * Class containing utils related to graph topology
 */
public class GraphUtils {
	
	/** Return a set of topology nodes, from a specified network topology
	 * @param networkData network topology
	 * @return a set of network nodes
	 */
	public static ArrayList<TopologyNode> extractNodesFromNetwork(HashMap<String, Object> networkData) {
		LinkedTreeMap<String, Object> vertices = (LinkedTreeMap<String, Object>) networkData.get("vertices");
		ArrayList<TopologyNode> retNodes = new ArrayList<TopologyNode>();
		
		for (String key : vertices.keySet()) {
			LinkedTreeMap<String, Object> info = (LinkedTreeMap<String, Object>) (vertices.get(key));
			
			LinkedTreeMap<String, Double> pos = (LinkedTreeMap<String, Double>) info.get("pos");
			
			info = (LinkedTreeMap<String, Object>) info.get("vertex_info");
			String type = (String) info.get("node-type");
			
			String name = key;
			if (((LinkedTreeMap<String, Object>) info.get("property")).get("custom_label") != "") {
				name = (String) ((LinkedTreeMap<String, Object>) info.get("property")).get("custom_label");
			}
			
			if (type.contains("-")) {
				type = type.replace("-", "");
			}
			
			TopologyNode tn = new TopologyNode(name, type);
			tn.setX(pos.get("x"));
			tn.setY(pos.get("y"));
			retNodes.add(tn);
		}
		
		return retNodes;
	}
	
	/** Return a set of topology edges, from a specified network topology
	 * @param networkData network topology
	 * @return a set of network edges
	 */
	public static ArrayList<TopologyEdge> extractEdgesFromNetwork(HashMap<String, Object> networkData) {
		LinkedTreeMap<String, Object> values = (LinkedTreeMap<String, Object>) networkData.get("edges");
		ArrayList<TopologyEdge> retEdges = new ArrayList<TopologyEdge>();
		
		for (String key : values.keySet()) {
			String[] split = key.split("&&");
			LinkedTreeMap<String, Object> preEdges = (LinkedTreeMap<String, Object>) values.get(key);
			ArrayList<LinkedTreeMap<String, String>> links = (ArrayList<LinkedTreeMap<String, String>>) preEdges.get("links");
			for (int ii = 0; ii < links.size(); ii++) {
				LinkedTreeMap<String, String> link = links.get(ii);
				String label = "";
				String type = "";
				double capacity = 1;
				double load = 0;
				for (String key_link : link.keySet()) {
					switch (key_link) {
						case "link_label": {
							label = link.get(key_link);
						}
						break;
						
						case "link-type":  {
							type = link.get(key_link);
						}
						break;
						
						case "link_capacity": {
							capacity = Double.parseDouble(link.get(key_link));
						}
						break;
						
						case "link_load":  {
							load = Double.parseDouble(link.get(key_link));
						}
						break;
					}
				}
				
				TopologyEdge te = new TopologyEdge(split[0], split[1], label, type, capacity, load);
				retEdges.add(te);
			}
		}
		
		return retEdges;
	}
	
	/** Return a set of topology nodes, from a specified TopologyCatalogue
	 * @param catalogue topology catalogue
	 * @return a set of network nodes
	 */
	public static ArrayList<TopologyNode> extractNodesFromTopologyCatalogue(TopologyCatalogue catalogue) {
		ArrayList<TopologyNode> retNodes = new ArrayList<TopologyNode>();
		ArrayList<String> tmp = new ArrayList<String>();
		
		for (TopologyCatalogueElement tce : catalogue) {
			if (!tmp.contains(tce.getSrc())) {
				TopologyNode tn = new TopologyNode(tce.getSrc(), GraphConstant.CORE_ROUTER);
				tn.setX(new Random().nextDouble() * 200.0);
				tn.setY(new Random().nextDouble() * 200.0);
				retNodes.add(tn);
				
				tmp.add(tce.getSrc());
			}
			
			if (!tmp.contains(tce.getDst())) {
				TopologyNode tn = new TopologyNode(tce.getDst(), GraphConstant.CORE_ROUTER);
				tn.setX(new Random().nextDouble() * 200.0);
				tn.setY(new Random().nextDouble() * 200.0);
				retNodes.add(tn);
				
				tmp.add(tce.getDst());
			}
		}
		
		return retNodes;
	}
	
	/** Return a set of topology edges, from a specified TopologyCatalogue
	 * @param catalogue topology catalogue
	 * @return a set of network edges
	 */
	public static ArrayList<TopologyEdge> extractEdgesFromTopologyCatalogue(TopologyCatalogue catalogue) {
		ArrayList<TopologyEdge> retEdges = new ArrayList<TopologyEdge>();
		
		for (TopologyCatalogueElement tce : catalogue) {
			String src = tce.getSrc();
			String dst = tce.getDst();
			String label = "";
			if (tce.getFeatures().getId() != null) {
				label = tce.getFeatures().getId();
			}
			else {
				label = src + dst + Integer.toString(new Random().nextInt(20000));
			}
			double capacity = tce.getFeatures().getCapacity();
			double load = tce.getFeatures().getAllocated();
			
			TopologyEdge te = new TopologyEdge(src, dst, label, "", capacity, load);
			retEdges.add(te);
		}
		
		return retEdges;
	}

}
