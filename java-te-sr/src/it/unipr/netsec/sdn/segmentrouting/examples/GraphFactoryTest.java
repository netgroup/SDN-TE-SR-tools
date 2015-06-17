package it.unipr.netsec.sdn.segmentrouting.examples;



import org.graphstream.graph.Graph;
import org.graphstream.ui.view.Viewer;



/** Graph factory test.
 */
public class GraphFactoryTest {

	
	/** No constructor is available. */
	public GraphFactoryTest() {
	}
	
		
	/** Main method. */
	public static void main(String[] args) {
		//Graph graph=NetworkGraphFactory.getTestNetworkGraph_1("TestNetworkGraph 1"); 		
		Graph graph=NetworkGraphFactory.getTestNetworkGraph_2("TestNetworkGraph 2"); 		
		//graph=NetworkGraph.copy(graph,"Copy of the graph");
		Viewer viewer=graph.display();
		viewer.disableAutoLayout();		
	}

}
