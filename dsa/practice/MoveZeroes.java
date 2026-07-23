import java.util.*;

public class MoveZeroes{

    // public static void moveZeroes(int[] nums){
    //     int[] newNums = new int [nums.length];
    //     int j = 0;
    //     for(int i = 0; i < nums.length; i++){
    //         if(nums[i] != 0){
    //             newNums[j] = nums[i];
    //             j++;
    //         }
    //     }
    //     for(int i = 0; i < nums.length; i++){
    //         if(i < newNums.length){
    //             nums[i] = newNums[i];
    //         }else{
    //             nums[i] = 0;
    //         }
    //     }

    // }

    public static void moveZeroes(int[] nums){
        int left = 0;
        for (int right = 0; right < nums.length; right++){
            if (nums[right] != 0 ){
                int temp = nums[right];
                nums[right] = nums[left];
                nums[left] = temp;
                left++;
            }
        }
    }


    public static void main(String [] args){
     int [] nums = {0,1,0,3,12};
     moveZeroes(nums);
     System.out.println(Arrays.toString(nums));
    }
}