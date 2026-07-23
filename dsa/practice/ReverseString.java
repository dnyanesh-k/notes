import java.util.*;

public class ReverseString{

    // public static char[] reverseString(char[] s) {
    //     char [] temp = new char[s.length];
    //     for(int i = s.length - 1, j = 0 ; i >= 0; i--, j++){
    //         temp[j] = s[i];
    //     }
    //     for(int i = 0 ; i < s.length; i++){
    //         s[i] = temp[i];
    //     }

    //     return s;
    // }

    // public static char [] reverseString(char [] s){
    //     List<Character> list = new ArrayList<>();
    //     for(char ch : s){
    //         list.add(ch);
    //     }
    //     Collections.reverse(list);

    //     for(int i = 0; i < s.length; i++){
    //         s[i] = list.get(i);
    //     }
    //     return s;
    // }

    public static char [] reverseString(char [] s){
        int left = 0;
        int right = s.length - 1;
        while(left < right){
            char temp = s[right];
            s[right] = s[left];
            s[left] = temp;
            left++;
            right--;
        }
        return s;
    }

    public static void main(String [] args){
        char[] s = {'h', 'e', 'l', 'l', 'o'};
       System.out.println(reverseString(s));
    }
}