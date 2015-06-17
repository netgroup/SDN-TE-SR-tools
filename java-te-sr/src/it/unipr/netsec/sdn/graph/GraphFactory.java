package it.unipr.netsec.sdn.graph;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import it.unipr.netsec.sdn.graph.element.TopologyCatalogue;
import it.unipr.netsec.sdn.graph.element.TopologyCatalogueElement;
import it.unipr.netsec.sdn.graph.element.TopologyCatalogueElementFeatures;
import it.unipr.netsec.sdn.graph.element.TopologyEdge;
import it.unipr.netsec.sdn.graph.element.TopologyNode;
import it.unipr.netsec.sdn.graph.util.GraphConstant;
import it.unipr.netsec.sdn.graph.util.GraphUtils;
import it.unipr.netsec.sdn.segmentrouting.SegmentRoutingCatalogue;
import it.unipr.netsec.sdn.trafficflow.element.FlowElement;
import it.unipr.netsec.sdn.trafficflow.element.TrafficFlowContainer;
import it.unipr.netsec.sdn.util.Utils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Random;

import org.graphstream.graph.*;
import org.graphstream.graph.implementations.*;
import org.graphstream.ui.graphicGraph.stylesheet.StyleConstants.Units;
import org.graphstream.ui.spriteManager.Sprite;
import org.graphstream.ui.spriteManager.SpriteManager;
import org.graphstream.ui.view.Viewer;

import com.google.gson.Gson;

/**
 * It allows to build and display a network topology onto a graph representation, using GraphStream library
 */
public class GraphFactory {
	
	private TopologyCatalogue topologyCatalogue;
	
	private ArrayList<TopologyNode> nodes;
	private ArrayList<TopologyEdge> edges;
	
	private Graph g = null;
	
	private boolean directedEdge = true;
	
	/** Contructor */
	public GraphFactory() {
		this.nodes = new ArrayList<TopologyNode>();
		this.edges = new ArrayList<TopologyEdge>();
		this.topologyCatalogue = new TopologyCatalogue();
	}
	
	/** Contructor
	 * @param topologyFile the topology file, in JSON format
	 */
	public GraphFactory(String topologyFile) {
		this();
		loadTopologyFromJSONFile(topologyFile);
		buildGraphStreamTopology();
	}
	
	/** Return the graph representation of the network topology
	 * @return the graph representation of the network topology
	 */
	public Graph getGraph() { return this.g; }
	
	public void setDirectedEdge(boolean directed) { this.directedEdge = directed; }
	public boolean isDirectedEdge() { return this.directedEdge; }
	
	private void loadTopologyFromJSONFile(String jsonFile) {
        HashMap<String, Object> networkData = Utils.readJSONFile(jsonFile);
        
        this.nodes = GraphUtils.extractNodesFromNetwork(networkData);
        this.edges = GraphUtils.extractEdgesFromNetwork(networkData);
	}
	
	/** Load a network topology from a JSON file, representing a TopologyCatalogue
	 * @param jsonFile the JSON TopologyCatalogue file
	 */
	public void loadTopologyCatalogueFromJSONFile(String jsonFile) {
		if (jsonFile == null) {
			System.err.println("[ERROR] No topology defined.");
			System.exit(-1);
		}
		
		ArrayList<Object> pairs = Utils.readJSONFileAsArrayList(jsonFile);
		this.topologyCatalogue = buildTopologyCatalogue(pairs);
		
		this.nodes = GraphUtils.extractNodesFromTopologyCatalogue(this.topologyCatalogue);
		this.edges = GraphUtils.extractEdgesFromTopologyCatalogue(this.topologyCatalogue);
	}
	
	public static TopologyCatalogue buildTopologyCatalogue(ArrayList<Object> pairs) {
		TopologyCatalogue topologyCatalogue = new TopologyCatalogue();
		for (Object obj : pairs) {
			ArrayList<Object> nodeJSON = (ArrayList<Object>) obj;
			String src = (String) nodeJSON.get(0);
			String dst = (String) nodeJSON.get(1);
			
			TopologyCatalogueElementFeatures tce = new Gson().fromJson(nodeJSON.get(2).toString(), TopologyCatalogueElementFeatures.class);
			
			topologyCatalogue.add(new TopologyCatalogueElement(src, dst, tce));
		}
		
		return topologyCatalogue;
	}
	
	public void buildGraphStreamTopology() {
		this.g = new MultiGraph("TestGraph");
		
		for (TopologyNode node : this.nodes) {
			Node n = this.g.addNode(node.getLabel());
			n.setAttribute(GraphConstant.ATTRIBUTE_NODE_TYPE, node.getType());
			n.setAttribute("x", node.getX());
			n.setAttribute("y", node.getY());
		}
		
		for (TopologyEdge edge : this.edges) {
			String id = edge.getLabel();
			Edge e = this.g.addEdge(id, edge.getV1(), edge.getV2(), directedEdge);
			e.addAttribute(GraphConstant.ATTRIBUTE_EDGE_LABEL, edge.getLabel());
			e.addAttribute(GraphConstant.ATTRIBUTE_EDGE_TYPE, edge.getType());
			e.addAttribute(GraphConstant.ATTRIBUTE_EDGE_CAPACITY, edge.getCapacity());
			e.addAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD, edge.getLoad());
		}
	}
	
	/**
	 * Display the network topology using a graph-based representation
	 * @param k the graph to be represented with the library
	 */
	public static void displayGraph(Graph k) {
		displayGraph(k, true);
	}
	
	/**
	 * Display the network topology using a graph-based representation
	 * @param k the graph to be represented with the library
	 * @param disableAutolayout manage the GraphStream autolayout
	 */
	public static void displayGraph(Graph k, boolean disableAutolayout) {
		if (k == null) {
			System.exit(-1);
		}
		
		String stylesheet = Utils.readFile("css/graph.css");
		
		k.addAttribute("ui.stylesheet", stylesheet);
		
		for (Node n : k.getNodeSet()) {
			n.addAttribute("ui.label", n.getId());
			String type = n.getAttribute(GraphConstant.ATTRIBUTE_NODE_TYPE);
			if (type.equals(GraphConstant.CORE_ROUTER)) {
				n.addAttribute("ui.class", "cro");
			}
			else if (type.equals(GraphConstant.CUSTOMER_EDGE_ROUTER)) {
				n.addAttribute("ui.class", "cer");
			}
			else if (type.equals(GraphConstant.PROVIDER_EDGE_ROUTER)) {
				n.addAttribute("ui.class", "per");
			}
		}
		
		for (Edge e : k.getEdgeSet()) {
			e.addAttribute("ui.label", e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD) + " / " + e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_CAPACITY));
		}
		
		System.setProperty("org.graphstream.ui.renderer", "org.graphstream.ui.j2dviewer.J2DGraphRenderer");
		
		Viewer viewer = k.display();
		
		if (disableAutolayout) {
			viewer.disableAutoLayout();
		}
	}
	
	/**
	 * Display the network topology using a POOR graph-based representation
	 * @param k the graph to be represented with the library
	 * @param disableAutolayout manage the GraphStream autolayout
	 */
	public static void displayPoorGraph(Graph k, boolean disableAutolayout) {
		if (k == null) {
			System.exit(-1);
		}
		
		String stylesheet = Utils.readFile("css/graph.css");
		
		k.addAttribute("ui.stylesheet", stylesheet);
		
		for (Node n : k.getNodeSet()) {
			String type = n.getAttribute(GraphConstant.ATTRIBUTE_NODE_TYPE);
			if (type.equals(GraphConstant.CORE_ROUTER)) {
				n.addAttribute("ui.class", "cro");
			}
			else if (type.equals(GraphConstant.CUSTOMER_EDGE_ROUTER)) {
				n.addAttribute("ui.class", "cer");
			}
			else if (type.equals(GraphConstant.PROVIDER_EDGE_ROUTER)) {
				n.addAttribute("ui.class", "per");
			}
		}
		
		System.setProperty("org.graphstream.ui.renderer", "org.graphstream.ui.j2dviewer.J2DGraphRenderer");
		
		Viewer viewer = k.display();
		
		if (disableAutolayout) {
			viewer.disableAutoLayout();
		}
	}
	
	/**
	 * Display the network topology using a graph-based representation
	 * @param k the graph to be represented with the library
	 * @param disableAutolayout manage the GraphStream autolayout
	 */
	public static void displayGraphWithFlows(Graph k, TrafficFlowContainer fc, boolean disableAutolayout) {
		if (k == null) {
			System.exit(-1);
		}
		
		String stylesheet = Utils.readFile("css/graph.css");
		
		k.addAttribute("ui.stylesheet", stylesheet);
		
		for (Node n : k.getNodeSet()) {
			n.addAttribute("ui.label", n.getId());
			String type = n.getAttribute(GraphConstant.ATTRIBUTE_NODE_TYPE);
			if (type.equals(GraphConstant.CORE_ROUTER)) {
				n.addAttribute("ui.class", "cro");
			}
			else if (type.equals(GraphConstant.CUSTOMER_EDGE_ROUTER)) {
				n.addAttribute("ui.class", "cer");
			}
			else if (type.equals(GraphConstant.PROVIDER_EDGE_ROUTER)) {
				n.addAttribute("ui.class", "per");
			}
		}
		
		HashMap<String, SpritePair> busy = new HashMap<>();
		for (Edge e : k.getEdgeSet()) {
			e.addAttribute("ui.label", e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD) + " / " + e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_CAPACITY));
			busy.put(e.getId(), new GraphFactory.SpritePair(1.0, false));
		}
		
		SpriteManager smgr = new SpriteManager(k);
		int spriteIdx = 1;
		double spriteDistance = 7.0;
		double spriteX = 1.0;
		for (FlowElement f : fc) {
			for (Edge e : f.getPath().getEdgeSet()) {
				Sprite sp = smgr.addSprite("sprite_" + e.getId() + "_" + Integer.toString(new Random().nextInt(15)));
				sp.attachToEdge(e.getId());
				double spriteY = busy.get(e.getId()).getSpritePos() * (-spriteDistance);
				if (busy.get(e.getId()).isSignChange()) {
					spriteY = -spriteY;
					busy.get(e.getId()).incrementSpritePos();
				}
				busy.get(e.getId()).switchsignChange();
				sp.setPosition(Units.PX, spriteX, spriteY, 0);
				sp.addAttribute("ui.class", "S" + spriteIdx);
			}
			if (spriteIdx <= 9) {
				spriteIdx++;
			}
			else {
				spriteIdx = 1;
			}
		}
		
		System.setProperty("org.graphstream.ui.renderer", "org.graphstream.ui.j2dviewer.J2DGraphRenderer");
		
		Viewer viewer = k.display();
		
		if (disableAutolayout) {
			viewer.disableAutoLayout();
		}
	}
	
	public void saveTopologyToTopologyCatalogue(Graph gr, TrafficFlowContainer fc) {
		for (Edge e : gr.getEdgeSet()) {
			String edgeID = e.getId();
			
			for (TopologyCatalogueElement tce : this.topologyCatalogue) {
				if (tce.getFeatures().getId().equals(edgeID)) {
					tce.getFeatures().setAllocated((double) e.getAttribute(GraphConstant.ATTRIBUTE_EDGE_LOAD));
					
					ArrayList<String> flowsSequence = new ArrayList<String>();
					for (FlowElement fe : fc) {
						for (Edge edgeInPath : fe.getPath().getEdgePath()) {
							if (edgeInPath.getId().equals(edgeID)) {
								flowsSequence.add(fe.getId());
							}
						}
					}
					tce.getFeatures().setFlows(flowsSequence.toArray(new String[]{}));
				}
			}
		}
	}
	
	public void saveTopologyToTopologyCatalogue(Graph gr, SegmentRoutingCatalogue srCatalogue, String topologyCatalogueJSONFile) {
		TrafficFlowContainer tfc = new TrafficFlowContainer();
		tfc.addAll(srCatalogue.getFlowElements());
		
		this.saveTopologyToTopologyCatalogue(gr, tfc);
		Utils.writeStringToJSONFile(this.topologyCatalogue.toString(), topologyCatalogueJSONFile);
	}
	
	static class SpritePair {
		double spritePos = 1;
		boolean signChange = false;

		public SpritePair(double spritePos, boolean signChange) {
			this.spritePos = spritePos;
			this.signChange = signChange;
		}
		
		public double getSpritePos() { return spritePos; }
		public void setSpritePos(double spritePos) { this.spritePos = spritePos; }
		public void incrementSpritePos() { this.spritePos++; }
		
		public boolean isSignChange() { return signChange; }
		public void setSignChange(boolean signChange) { this.signChange = signChange; }
		public void switchsignChange() { this.signChange = !this.signChange; }
	}
	
}
