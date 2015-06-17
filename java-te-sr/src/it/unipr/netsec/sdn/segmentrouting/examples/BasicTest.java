package it.unipr.netsec.sdn.segmentrouting.examples;



import it.unipr.netsec.sdn.segmentrouting.*;

import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.Path;
import org.graphstream.ui.view.Viewer;



/** Basic Segment Routing test.
 */
public class BasicTest {

	
	/** Gets a string representation of a path.
	 * @param path the path*/
	/*public static String pathToString(Path path) {
		StringBuffer sb=new StringBuffer();
		for (Node node : path.getNodePath()) {
			if (sb.length()>0) sb.append(',');
			sb.append(node.getId());
		}
		return sb.toString();
	}*/

	
	/** Waits for a given number of milliseconds.
	 * @param millisecs number of milliseconds to wait */
	static void sleep(long millisecs) {
		try { Thread.sleep(millisecs); } catch (Exception e) {}
	}

		
	/** Prints a message.
	 * @param str the string to be printed */
	public static void println(String str) {
		System.out.println(str);
	}

		
	/** Main method.
	 * @param args command-line parameters */
	public static void main(String[] args) {
		//System.setProperty("org.graphstream.ui.renderer", "org.graphstream.ui.j2dviewer.J2DGraphRenderer");
		//System.setProperty("gs.ui.renderer", "org.graphstream.ui.j2dviewer.J2DGraphRenderer");

		Graph graph=NetworkGraphFactory.getTestNetworkGraph_1("Test 1"); 
		//String[] path_edges={"AG","AB","BC","CE","EF","FH"};
		//String[] path_edges={"AG","AD","DE","CE","CF","FH"};
		String[] path_edges={"GA","AB","BC","CE","EF","FH"};
		Path assigned_path=NetworkGraph.getPath(graph,path_edges);
		
		//Graph graph=NetworkGraphFactory.getTestNetworkGraph_2("Test 2"); 
		//String[] path_edges={"AB","BC","CD","DE"};
		//Path assigned_path=NetworkGraph.getPath(graph,path_edges);
		
		//graph=GraphFactory.copy(graph,"Copy");
		Viewer viewer=graph.display();
		viewer.disableAutoLayout();
		
		/*SpriteManager sman=new SpriteManager(graph);
		Sprite s=sman.addSprite("S1");
		s.attachToEdge("AB");
		s.setPosition(0.5);*/
		
		println("assigned path: "+assigned_path);
		println("natural path: "+SegmentRouting.getNaturalPath(graph,NetworkGraph.getPathSource(assigned_path).getId(),NetworkGraph.getPathDestination(assigned_path).getId()));
		
		try {
			Node[] segments=SegmentRouting.getSegments(graph,assigned_path);
			System.out.print("segments:");
			for (Node segment : segments) {
				System.out.print(" "+segment.getId());
			}
			System.out.println();
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}

}
