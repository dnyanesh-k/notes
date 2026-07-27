import java.util.*;

public class ArrayListDemo{
    public static void main(String [] args){
            ArrayList a = new ArrayList();
            a.add("A");
            a.add(10);
            a.add("A");
            a.add(null);
            a.add(false);
            System.out.println(a);
            // a.remove(2);
            a.remove("A");
            System.out.println(a);
            a.add(2, "M");
            a.add("N");
            System.out.println(a);
    }
}