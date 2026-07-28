import java.util.*;

public class ListIteratorDemo{
    public static void main(String [] args){
        LinkedList list = new LinkedList();
        list.add("Soham");
        list.add("Kanke");
        list.add("Omkar");
        list.add("Dhanu");
        System.out.println(list);

        ListIterator itr = list.listIterator();
        while(itr.hasNext()){
            String str = (String) itr.next();
            System.out.println(str);
            if(str.equals("Kanke")){
                itr.remove();
            }
            if(str.equals("Dhanu")){
                itr.set("Dhanashree");
            }
        }
        while(itr.hasNext()){
            String s = (String) itr.next();
            if(!s.equals("Shivu")){
                itr.add("Shivu");
            }
        }
        System.out.println(list);
    }
}
