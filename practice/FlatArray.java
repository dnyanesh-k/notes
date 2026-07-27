import java.util.*;

public class FlatArray{

    public static void main(String [] args){
        // int [][] nestedArray = {{1,2,3},{4,5},{6,7,8}};

        // int [] flatArray = Arrays.stream(nestedArray)
        //                          .flatMapToInt(Arrays::stream)
        //                          .toArray();

        // System.out.println(Arrays.toString(flatArray));
       final int [] arr = {1,2,3};
       arr[0] = 10;

       System.out.println(arr[0]);
    }
}