import java.util.*;
public class TreeSetDemo{
    public static void main(String [] args){
        TreeSet ts = new TreeSet(new MyComparator());
        ts.add(10);
        ts.add(0);
        ts.add(5);
        ts.add(15);
        ts.add(20);
        System.out.println(ts);
    }
}

class MyComparator implements Comparator{
      public int compare(Object o1 , Object o2){
        Integer i1 = (Integer) o1;
        Integer i2 = (Integer) o2;
        if(i1<i2){
            return  +1;
        }else if(i1 > i2){
            return -1;
        }else{
            return 0;
        }
      }
}