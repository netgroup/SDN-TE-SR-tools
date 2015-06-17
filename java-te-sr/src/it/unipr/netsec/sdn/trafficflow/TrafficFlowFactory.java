package it.unipr.netsec.sdn.trafficflow;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import it.unipr.netsec.sdn.graph.GraphFactory;
import it.unipr.netsec.sdn.graph.element.TopologyNode;
import it.unipr.netsec.sdn.graph.util.GraphUtils;
import it.unipr.netsec.sdn.segmentrouting.SegmentRoutingCatalogue;
import it.unipr.netsec.sdn.trafficflow.element.FlowCatalogue;
import it.unipr.netsec.sdn.trafficflow.element.FlowCatalogueElement;
import it.unipr.netsec.sdn.trafficflow.element.FlowCatalogueElementFeatures;
import it.unipr.netsec.sdn.trafficflow.element.FlowElement;
import it.unipr.netsec.sdn.trafficflow.element.TrafficFlowContainer;
import it.unipr.netsec.sdn.util.Utils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Random;

import org.graphstream.graph.Node;

import com.google.gson.Gson;

/**
 * Factory for traffic flow elements
 */
public class TrafficFlowFactory {
	
	private TrafficFlowContainer trafficFlowsContainer = null;
	
	private FlowCatalogue flowCatalogue = new FlowCatalogue();
	
	/** Constructor */
	public TrafficFlowFactory() {
		this.trafficFlowsContainer = new TrafficFlowContainer();
	}

	/** Constructor
	 * @param topologyFile the JSON topology file
	 * @param trafficFlowFile the JSON traffic flows file
	 */
	public TrafficFlowFactory(String topologyFile, String trafficFlowFile) {
		this();
		loadFlowCatalogueFromJSONFile(trafficFlowFile);
	}
	
	/** Load a FlowCatalogue from a JSON file
	 * @param jsonFile the JSON FlowCatalogue file
	 */	
	public void loadFlowCatalogueFromJSONFile(String jsonFile) {
		if (jsonFile == null) {
			System.err.println("[ERROR] No FlowCatalogue file defined.");
			System.exit(-1);
		}
		
		HashMap<String, Object> flowArray = Utils.readJSONFile(jsonFile);		
		for (String key : flowArray.keySet()) {
			ArrayList<Object> flowJSON = (ArrayList<Object>) flowArray.get(key);
			FlowCatalogueElementFeatures fcef = new Gson().fromJson(new Gson().toJson(flowJSON.get(2)), FlowCatalogueElementFeatures.class);
			
			if (fcef.getOut() != null) {
				String src = (String) flowJSON.get(0);
				String dst = (String) flowJSON.get(1);
				double bandwidth = fcef.getOut().getSize();
				
				String flowID = "";
				if (fcef.getId() != null) {
					flowID = fcef.getId() + "_out";
				}
				else {
					flowID = src + dst + Integer.toString(new Random().nextInt(20000)) + "_out";
				}
				
				FlowElement fe = new FlowElement(flowID, src, dst, bandwidth);
				fe.setRelationID(key);
				fe.setRelationType(FlowElement.OUT);
				this.trafficFlowsContainer.add(fe);
				
				FlowCatalogueElement fce = new FlowCatalogueElement(src, dst, fcef);
				this.flowCatalogue.put(key + "_out", fce);
			}
			
			if (fcef.getIn() != null) {
				String src = (String) flowJSON.get(1);
				String dst = (String) flowJSON.get(0);
				double bandwidth = fcef.getIn().getSize();
				
				String flowID = "";
				if (fcef.getId() != null) {
					flowID = fcef.getId() + "_in";
				}
				else {
					flowID = src + dst + Integer.toString(new Random().nextInt(20000)) + "_in";
				}
				
				FlowElement fe = new FlowElement(flowID, src, dst, bandwidth);
				fe.setRelationID(key);
				fe.setRelationType(FlowElement.IN);
				this.trafficFlowsContainer.add(fe);
				
				FlowCatalogueElement fce = new FlowCatalogueElement(src, dst, fcef);
				this.flowCatalogue.put(key + "_in", fce);
			}
		}
	}
	
	/** Load a FlowCatalogue from a JSON file
	 * @param jsonFile The JSON FlowCatalogue file
	 * @param flowUpperBound Max number of flows that has to be loaded
	 */
	public void loadFlowCatalogueFromJSONFile(String jsonFile, int flowUpperBound) {
		if (jsonFile == null) {
			System.err.println("[ERROR] No FlowCatalogue file defined.");
			System.exit(-1);
		}
		
		this.trafficFlowsContainer = new TrafficFlowContainer();
		
		int count = 0;
		
		HashMap<String, Object> flowArray = Utils.readJSONFile(jsonFile);		
		for (String key : flowArray.keySet()) {
			ArrayList<Object> flowJSON = (ArrayList<Object>) flowArray.get(key);
			FlowCatalogueElementFeatures fcef = new Gson().fromJson(new Gson().toJson(flowJSON.get(2)), FlowCatalogueElementFeatures.class);
			
			if (fcef.getOut() != null) {
				String src = (String) flowJSON.get(0);
				String dst = (String) flowJSON.get(1);
				double bandwidth = fcef.getOut().getSize();
				
				String flowID = "";
				if (fcef.getId() != null) {
					flowID = fcef.getId() + "_out";
				}
				else {
					flowID = src + dst + Integer.toString(new Random().nextInt(35)) + "_out";
				}
				
				FlowElement fe = new FlowElement(flowID, src, dst, bandwidth);
				fe.setRelationID(key);
				fe.setRelationType(FlowElement.OUT);
				this.trafficFlowsContainer.add(fe);
				
				FlowCatalogueElement fce = new FlowCatalogueElement(src, dst, fcef);
				this.flowCatalogue.put(key, fce);
				
				count ++;
				if (count == flowUpperBound) {
					return;
				}
			}
			
			if (fcef.getIn() != null) {
				String src = (String) flowJSON.get(1);
				String dst = (String) flowJSON.get(0);
				double bandwidth = fcef.getIn().getSize();
				
				String flowID = "";
				if (fcef.getId() != null) {
					flowID = fcef.getId() + "_in";
				}
				else {
					flowID = src + dst + Integer.toString(new Random().nextInt(35)) + "_in";
				}
				
				FlowElement fe = new FlowElement(flowID, src, dst, bandwidth);
				fe.setRelationID(key);
				fe.setRelationType(FlowElement.IN);
				this.trafficFlowsContainer.add(fe);
				
				FlowCatalogueElement fce = new FlowCatalogueElement(src, dst, fcef);
				this.flowCatalogue.put(key, fce);
				
				count ++;
				if (count == flowUpperBound) {
					return;
				}
			}
		}
	}
	
	public void saveTrafficFlowToFlowCatalogue(SegmentRoutingCatalogue srCatalogue, String trafficFlowJSONFile) {
		TrafficFlowContainer tfc = new TrafficFlowContainer();
		tfc.addAll(srCatalogue.getFlowElements());
		
		FlowCatalogue tmp = new FlowCatalogue();
		for (String key : this.flowCatalogue.keySet()) {
			if (key.contains("_out")) {
				String realKey = key.substring(0, key.indexOf("_out"));
				if (!tmp.containsKey(realKey)) {
					tmp.put(realKey, new FlowCatalogueElement(this.flowCatalogue.get(key).getSrc(), this.flowCatalogue.get(key).getDst(), new FlowCatalogueElementFeatures()));
				}
				tmp.get(realKey).getFeatures().setOut(this.flowCatalogue.get(key).getFeatures().getOut());
				tmp.get(realKey).getFeatures().setId(this.flowCatalogue.get(key).getFeatures().getId());
				tmp.get(realKey).setSrc(this.flowCatalogue.get(key).getSrc());
				tmp.get(realKey).setDst(this.flowCatalogue.get(key).getDst());
			}
			if (key.contains("_in")) {
				String realKey = key.substring(0, key.indexOf("_in"));
				if (!tmp.containsKey(realKey)) {
					tmp.put(realKey, new FlowCatalogueElement(this.flowCatalogue.get(key).getSrc(), this.flowCatalogue.get(key).getDst(), new FlowCatalogueElementFeatures()));
				}
				tmp.get(realKey).getFeatures().setIn(this.flowCatalogue.get(key).getFeatures().getIn());
				tmp.get(realKey).getFeatures().setId(this.flowCatalogue.get(key).getFeatures().getId());
				tmp.get(realKey).setSrc(this.flowCatalogue.get(key).getDst());
				tmp.get(realKey).setDst(this.flowCatalogue.get(key).getSrc());
			}
		}
		
		Utils.writeStringToJSONFile(tmp.toString(), trafficFlowJSONFile);
	}
	
	public void addSegmentsToTrafficFlow(FlowElement fe, Node[] segments) {
		for (String key : this.flowCatalogue.keySet()) {
			FlowCatalogueElement fce = this.flowCatalogue.get(key);
			String flowID = fce.getFeatures().getId();
			if (fe.getId().contains(flowID)) {
				ArrayList<String> segmentsArrayList = new ArrayList<String>();
				for (int jj = 0;jj < segments.length; jj++) {
					segmentsArrayList.add(segments[jj].getId());
				}
				
				//if (fe.getId().contains("_in")) {
				if (fe.getRelationType().equals(FlowElement.IN)) {
					fce.getFeatures().getIn().setPath(segmentsArrayList.toArray(new String[]{}));
					fce.getFeatures().getIn().setAllocated(true);
					return;
				}
				
				//if (fe.getId().contains("_out")) {
				if (fe.getRelationType().equals(FlowElement.OUT)) {
					fce.getFeatures().getOut().setPath(segmentsArrayList.toArray(new String[]{}));
					fce.getFeatures().getOut().setAllocated(true);
					return;
				}
			}
		}
	}
	
	/** Generate random flows, based on the previously loaded topology
	 * @param numFlows the amount of traffic flows that has to be randomly generated
	 */
	public void generateRandomTrafficFlows(int numFlows, String nodesJSONFile) {
		this.trafficFlowsContainer = new TrafficFlowContainer();
		
		if (nodesJSONFile == null) {
			System.err.println("[ERROR] No topology file defined.");
			System.exit(-1);
		}
		
		ArrayList<Object> pairs = Utils.readJSONFileAsArrayList(nodesJSONFile);
		ArrayList<TopologyNode> nodes = GraphUtils.extractNodesFromTopologyCatalogue(GraphFactory.buildTopologyCatalogue(pairs));
		
		for (int ii = 0; ii < numFlows; ii++) {
			int srcIdx = new Random().nextInt(nodes.size());
			String src = nodes.get(srcIdx).getLabel();
			
			int destIdx = -1;
			while ((destIdx >= 0) && (destIdx != srcIdx)) {
				destIdx = new Random().nextInt(nodes.size());
			}
			String dest = nodes.get(destIdx).getLabel();
			
			double traffic = new Random().nextDouble() * 110;
			
			String id = src + dest + Integer.toString(new Random().nextInt(2000));
			
			FlowElement f = new FlowElement(id, src, dest, traffic);
			this.trafficFlowsContainer.add(f);
		}
	}
	
	/** Store traffic flows in a JSON file
	 * @param file the name of the file in which store the traffic flows
	 */
	public void writeFlowsOnFile(String file) {
		if (file == null) {
			System.err.println("[ERROR] No output traffic flow file defined.");
			System.exit(-1);
		}
		
		HashMap<String, ArrayList<FlowElement>> tmp = new HashMap<>();
		tmp.put("flows", this.trafficFlowsContainer);
		Utils.writeJSONFile(tmp, file);
	}
	
	/** Return the traffic flows
	 * @return the traffic flows
	 */
	public TrafficFlowContainer getTrafficFlows() { return this.trafficFlowsContainer; }
	
	/** Return the traffic flows catalogue
	 * @return the traffic flows catalogue
	 */
	public FlowCatalogue getFlowCatalogue() { return this.flowCatalogue; }
	
}
