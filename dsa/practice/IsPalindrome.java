public class IsPalindrome{

//    public static boolean isPalindrome(String s){
     
//      int left = 0;
//      int right = s.length() - 1;
//      System.out.println(right);
//      while (left < right){
//         while (left < right && !Character.isLetterOrDigit(s.charAt(left))){
//          left++;
//         }

//         while (left < right && !Character.isLetterOrDigit(s.charAt(right))){
//             right--;
//         }

//         if (Character.toLowerCase(s.charAt(left)) != Character.toLowerCase(s.charAt(right))){
//             return false;
//         }
//         left++;
//         right--;
//      }
//      return true;

//    }

      public static boolean isPalindrome(String s){
        StringBuilder newStr = new StringBuilder();
        for(char ch : s.toCharArray()){
           if(Character.isLetterOrDigit(ch)){
            newStr.append(Character.toLowerCase(ch));
           }
        }
        return newStr.toString().equals(newStr.reverse().toString());

      }
   public static void main(String [] args){
         String s = "0A man, a plan, a canal: Panama0";
         boolean isPalindrome = isPalindrome(s);
         System.out.println(isPalindrome);
    
   }
}