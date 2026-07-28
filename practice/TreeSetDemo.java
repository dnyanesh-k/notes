import java.util.*;
public class TreeSetDemo{
    public static void main(String [] args){
        TreeSet ts = new TreeSet(new MyComparator());
        ts.add("Soham");
        ts.add("Shivu");
        ts.add("Omkar");
        ts.add("Dhanu");
        ts.add("Divya");
        System.out.println(ts);
    }
}

class MyComparator implements Comparator{
      public int compare(Object o1 , Object o2){
        // Integer i1 = (Integer) o1;
        // Integer i2 = (Integer) o2;
        // if(i1<i2){
        //     return  +1;
        // }else if(i1 > i2){
        //     return -1;
        // }else{
        //     return 0;
        // }
        String s1 = o1.toString();
        String s2 = (String) o2;
        return -s1.compareTo(s2);
      }
}