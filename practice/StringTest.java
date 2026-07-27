public class StringTest{

     public static void main(String [] args){
        String str = "Soham";

        String str1 = new String("Soham");

        System.out.println(str == str1 );
        System.out.println(str.equals(str1));
        
        // str += "Kanke";
        str.concat("Kanke");
        System.out.println("After concate() ==> " + str);
        str = str.concat(" Kanke");
        System.out.println("After Reassignment ==> " + str);
        // System.out.println(str == str1 );
        // System.out.println(str.equals(str1));

        StringBuffer sb = new StringBuffer("Soham");
        sb.append(" Kanke");
        System.out.println("After concate SB ==> " + sb);
     }
}