package it.unipr.netsec.sdn.segmentrouting;

import java.util.ArrayList;
import java.util.Random;


/** Collection of methods for manipulating lists.
 */
public class ListUtils {

	public static Random RAND=new Random(0);

	
	/** Gets a sub-list.
	 * @param list the source list
	 * @param begin the sequence number of the first element
	 * @param end the sequence number of the last element + 1
	 * @return the sub-list */
	public static <T> ArrayList<T> subList(ArrayList<T> list, int begin, int end) {
		ArrayList<T> sublist=new ArrayList<T>();
		if (list.size()<end) end=list.size();
		for (int i=begin; i<end; i++) {
			T elem_i=list.get(i);
			sublist.add(elem_i);
		}
		return sublist;
	}


	/** Gets a scrambled version a list.
	 * The resulting list is a random permutation of the source list.
	 * @param list the source list
	 * @return the sub-list */
	public static <T> ArrayList<T> scrambledList(ArrayList<T> list) {
		/*ArrayList<T> aux_list=subList(list,0,list.size());
		ArrayList<T> scrambled_list=new ArrayList<T>();
		for (int i=0; i<list.size(); i++) {
			int j=RAND.nextInt(aux_list.size());
			T elem_i=aux_list.get(j);
			aux_list.remove(j);
			scrambled_list.add(elem_i);
		}
		return scrambled_list;*/
		return randomSubList(list,list.size());
	}


	/** Gets a random sub-list.
	 * The element of the sub-list are randomly taken from the source list. 
	 * @param list the source list
	 * @param size the size of the sub-list
	 * @return the sub-list */
	public static <T> ArrayList<T> randomSubList(ArrayList<T> list, int size) {
		ArrayList<T> aux_list=subList(list,0,list.size());
		ArrayList<T> random_list=new ArrayList<T>();
		for (int i=0; i<size; i++) {
			int j=RAND.nextInt(aux_list.size());
			T elem_i=aux_list.get(j);
			aux_list.remove(j);
			random_list.add(elem_i);
		}
		return random_list;
	}
	
}
