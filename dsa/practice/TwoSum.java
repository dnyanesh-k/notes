import java.util.*;

public class TwoSum{

    // public static int[] twoSum(int[] numbers, int target){
    //    for(int i = 0; i < numbers.length; i++){
    //     for(int j = i + 1; j < numbers.length; j++){
    //         if((numbers[i] + numbers[j]) == target){
    //             return new int [] {numbers[i], numbers[j]};
    //         }
    //     }
    //    }
    //     return new int [] {};
    // } 
    public static int[] twoSum(int[] numbers, int target){
        HashMap<Integer, Integer> map = new HashMap<>();
        for(int i = 0; i < numbers.length; i++){
            int complement = target - numbers[i];
            if(map.containsKey(complement)){
                return new int [] {complement, numbers[i]};
            }
            map.put(numbers[i], i);
        }
        return new int [] {};

    } 
    public static void main(String [] args){
    int [] numbers = {2,7,11,15};
    int [] result = twoSum(numbers , 17);
    for(int i : result){
    System.out.println(i);
    }

    }
}