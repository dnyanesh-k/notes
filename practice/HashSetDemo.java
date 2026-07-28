import java.util.*;
public class HashSetDemo{
    public static void main(String [] args){
        LinkedHashSet hs = new LinkedHashSet();
        hs.add(1);
        hs.add("A");
        hs.add("B");
        hs.add("C");
        hs.add(null);
        System.out.println(hs.add("C"));
        System.out.println(hs);
    }
}