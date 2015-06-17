package it.unipr.netsec.sdn.util;

/*
*
* @author Luca Davoli - <a href="mailto:lucadavo@gmail.com">lucadavo@gmail.com</a> - Department of Information Engineering - University of Parma
*
*/

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

import com.google.gson.Gson;

/** Utils class */
public class Utils {
	
	public static final String CMDPARAMS_TOPO_IN = "topo_in";
	public static final String CMDPARAMS_TOPO_OUT = "topo_out";
	public static final String CMDPARAMS_FLOWS_IN = "flows_in";
	public static final String CMDPARAMS_FLOWS_OUT = "flows_out";
	public static final String CMDPARAMS_DEBUG = "debug";
	
	/** Open a JSON file and return its content 
	 * @param jsonFile the name of the file to be opened
	 * @return the file content, in a HashMap-like way
	 */
	public static HashMap<String, Object> readJSONFile(String jsonFile) {
		HashMap<String, Object> f = null;
		try {
			BufferedReader br = new BufferedReader(new FileReader(jsonFile));
			f = new Gson().fromJson(br, HashMap.class);
		}
		catch (FileNotFoundException e) {
			e.printStackTrace();
		}
		
		return f;
	}
	
	/** Open a JSON file and return its content as ArrayList of Object
	 * @param jsonFile the name of the file to be opened
	 * @return the file content, in a ArrayList-like way
	 */
	public static ArrayList<Object> readJSONFileAsArrayList(String jsonFile) {
		ArrayList<Object> f = new ArrayList<Object>();
		try {
			BufferedReader br = new BufferedReader(new FileReader(jsonFile));
			f = new Gson().fromJson(br, ArrayList.class);
		}
		catch (FileNotFoundException e) {
			e.printStackTrace();
		}
		
		return f;
	}
	
	public static String readFile(String file) {
		String content = "";
		try {
			BufferedReader br = new BufferedReader(new FileReader(file));
	    
	        StringBuilder sb = new StringBuilder();
	        String line = br.readLine();

	        while (line != null) {
	            sb.append(line);
	            sb.append(System.lineSeparator());
	            line = br.readLine();
	        }
	        
	        content = sb.toString();
	        
	        br.close();
	    }
		catch (Exception e) {
			e.printStackTrace();
		}
	    
	    return content;
	}
	
	/** Write the object content, treated with new GSon().toJson(), in a JSON file
	 * @param obj the object to be written
	 * @param jsonFile the name of the file
	 */
	public static void writeJSONFile(Object obj, String jsonFile) {
		String toWrite = new Gson().toJson(obj);
		
		try {
			FileWriter fw = new FileWriter(new File(jsonFile));
			fw.write(toWrite);
			fw.flush();
			fw.close();
		}
		catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	/** Write the object content, treated with toString(), in a JSON file
	 * @param obj the object to be written
	 * @param jsonFile the name of the file
	 */
	public static void writeStringToJSONFile(Object obj, String jsonFile) {
		if (jsonFile != null) { 
			String toWrite = obj.toString();
			
			try {
				FileWriter fw = new FileWriter(new File(jsonFile));
				fw.write(toWrite);
				fw.flush();
				fw.close();
			}
			catch (IOException e) {
				e.printStackTrace();
			}
		}
	}
	
	/** Parse the command-line and return a list of parameters
	 * @param args the command-line arguments
	 * @return a list of parameters, in a <key,value> fashion
	 */
	public static CMDParams parseCMD(String[] args) {
		CMDParams tmp = new CMDParams();
		for (String s : args) {
			String[] cmd = s.split("=");
			tmp.put(cmd[0].toLowerCase(), cmd[1]);
		}
		
		return tmp;
	}

}
