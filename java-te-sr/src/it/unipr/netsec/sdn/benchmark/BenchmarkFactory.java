package it.unipr.netsec.sdn.benchmark;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import java.io.BufferedWriter;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.util.Map;
import java.util.TreeMap;

import it.unipr.netsec.sdn.segmentrouting.SegmentRoutingCatalogue;
import it.unipr.netsec.sdn.trafficflow.element.FlowElement;

public class BenchmarkFactory {
	
	public static void histogram(SegmentRoutingCatalogue src, String nodeNum, String flowsNum) {
		Map<Integer, Integer> assigned = new TreeMap<Integer, Integer>();
		Map<Integer, Integer> natural = new TreeMap<Integer, Integer>();
		Map<Integer, Integer> segments = new TreeMap<Integer, Integer>();
		
		natural.put(0, 0);
		
		for (FlowElement fe : src.getFlowElements()) {
			String flowID = fe.getId();
			int size;
			
			// Assigned path
			size = src.getAssignedPath(flowID).size();
			if (assigned.containsKey(size)) {
				int count = assigned.get(size);
				count ++;
				assigned.put(size, count);
			}
			else {
				assigned.put(size, 1);
			}
			
			// Natural path
			if (size > 0) {
				size = src.getNaturalPath(flowID).size();
			}
			if (natural.containsKey(size)) {
				int count = natural.get(size);
				count ++;
				natural.put(size, count);
			}
			else {
				natural.put(size, 1);
			}
			
			// Segments
			size = src.getSegments(flowID).length;
			if (segments.containsKey(size)) {
				int count = segments.get(size);
				count ++;
				segments.put(size, count);
			}
			else {
				segments.put(size, 1);
			}
		}
		
		try {
			PrintWriter writerHistogramAssigned = new PrintWriter("log/histogram_assigned_" + nodeNum + "nodes_" + flowsNum + "flows.dat", "UTF-8");
			PrintWriter writerHistogramNatural = new PrintWriter("log/histogram_natural_" + nodeNum + "nodes_" + flowsNum + "flows.dat", "UTF-8");
			PrintWriter writerHistogramSegments = new PrintWriter("log/histogram_segments_" + nodeNum + "nodes_" + flowsNum + "flows.dat", "UTF-8");
			
			// Index \t Number_of_occurrences
			for (Integer key : assigned.keySet()) {
				writerHistogramAssigned.println(key + "\t" + assigned.get(key));
			}
			for (Integer key : natural.keySet()) {
				writerHistogramNatural.println(key + "\t" + natural.get(key));
			}
			for (Integer key : segments.keySet()) {
				writerHistogramSegments.println(key + "\t" + segments.get(key));
			}
			writerHistogramAssigned.close();
			writerHistogramNatural.close();
			writerHistogramSegments.close();
		}
		catch (FileNotFoundException | UnsupportedEncodingException e) {
			e.printStackTrace();
		}
	}
	
	public static void average(SegmentRoutingCatalogue src) {
		average(src, null, null, null, null, false);
	}
	
	public static void average(SegmentRoutingCatalogue src, String nodeNum, String flowsNum, String averageFileName, String allocatedFlowsCountFilename, boolean append) {
		double avgAssigned = 0.0;
		double avgNatural = 0.0;
		double avgSegments = 0.0;
		
		int count = 0;
		
		for (FlowElement fe : src.getFlowElements()) {
			String flowID = fe.getId();
			
			int sizeAssigned = src.getAssignedPath(flowID).size();
			int sizeNatural = src.getNaturalPath(flowID).size();
			int sizeSegments = src.getSegments(flowID).length;
			if ((sizeAssigned > 0) && (sizeSegments > 0)) {
				avgAssigned = incrementalAverageIteration(avgAssigned, sizeAssigned, count);
				avgNatural = incrementalAverageIteration(avgNatural, sizeNatural, count);
				avgSegments = incrementalAverageIteration(avgSegments, sizeSegments, count);
				
				count++;
			}
		}
		
		if (averageFileName == null) {
			System.out.println("Assigned: " + avgAssigned + " @ " + count);
			System.out.println("Natural: " + avgNatural + " @ " + count);
			System.out.println("Segments: " + avgSegments + " @ " + count);
		}
		else {
			try {
				// Averages lengths
				// nodeNum \t flowsNum \t avgAssigned \t avgNatural \t avgSegments
				PrintWriter writerAverageLengths = null;
				if (append == true) {
					writerAverageLengths = new PrintWriter(new BufferedWriter(new FileWriter(averageFileName, true)));
					writerAverageLengths.println(nodeNum + "\t" + flowsNum + "\t" + avgAssigned+ "\t" + avgNatural+ "\t" + avgSegments);
				}
				else {
					writerAverageLengths = new PrintWriter("log/average_length_" + nodeNum + "nodes_" + flowsNum + "flows.dat", "UTF-8");
					writerAverageLengths.println(nodeNum + "\t" + flowsNum + "\t" + avgAssigned+ "\t" + avgNatural+ "\t" + avgSegments);
				}
				writerAverageLengths.close();
				
				// Allocated flows
				// nodeNum \t flowsNum \t countAllocated
				PrintWriter writerCountAllocated = null;
				if (append == true) {
					writerCountAllocated = new PrintWriter(new BufferedWriter(new FileWriter(allocatedFlowsCountFilename, true)));
					writerCountAllocated.println(nodeNum + "\t" + flowsNum + "\t" + count);
				}
				else {
					writerCountAllocated = new PrintWriter("log/right_allocated_" + nodeNum + "nodes_" + flowsNum + "flows.dat", "UTF-8");
					writerCountAllocated.println(nodeNum + "\t" + flowsNum + "\t" + count);
				}
				writerCountAllocated.close();
			}
			catch (IOException e) {
				e.printStackTrace();
			}
		}
	}
	
	public static void times(TreeMap<String, Long> times) {
		times(times, null, null, null, false);
	}
	
	public static void times(TreeMap<String, Long> times, String nodeNum, String flowsNum, String filename, boolean append) {
		if (filename == null) {
			System.out.println("Time Assigned: " + times.get("assigned"));
			System.out.println("Time Natural: " + times.get("natural"));
			System.out.println("Time Segments: " + times.get("segments"));
		}
		else {
			try {
				// Times
				// nodeNum \t flowsNum \t timeAssigned \t timeNatural \t timeSegments
				PrintWriter writerExecutionTimes = null;
				if (append == true) {
					writerExecutionTimes = new PrintWriter(new BufferedWriter(new FileWriter(filename, true)));
					writerExecutionTimes.println(nodeNum + "\t" + flowsNum + "\t" + times.get("assigned")+ "\t" + times.get("natural") + "\t" + times.get("segments"));
				}
				else {
					writerExecutionTimes = new PrintWriter("log/average_length_" + nodeNum + "nodes_" + flowsNum + "flows.dat", "UTF-8");
					writerExecutionTimes.println(nodeNum + "\t" + flowsNum + "\t" + times.get("assigned")+ "\t" + times.get("natural") + "\t" + times.get("segments"));
				}
				writerExecutionTimes.close();
			}
			catch (IOException e) {
				e.printStackTrace();
			}
		}
	}
	
	public static double incrementalAverageIteration(double previousAverage, double value, int iterationIndex) {
		return ((value - previousAverage) / (iterationIndex + 1)) + previousAverage;
    }

}
