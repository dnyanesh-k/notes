import java.util.*;

public class LinkedListDemo{
    public static void main(String [] args){
        LinkedList list = new LinkedList();
        list.add("Soham");
        list.add(10);
        list.add(false);
        list.add(null);
        System.out.println(list);
        list.set(3,"canVote");
        System.out.println(list);
        list.addFirst("SOHAM");
        System.out.println(list);
        String first = (String) list.removeFirst();
        System.out.println(first);
        System.out.println(list);
    }
}