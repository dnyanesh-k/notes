import java.util.*;

public class StackDemo{
    public static void main(String [] args){
        Stack stack = new Stack();
        stack.push(10);
        stack.push("Soham");
        stack.push("Kanke");
        stack.push(false);
        stack.push("dnyaneshwar");
        
        System.out.println(stack.pop());
        System.out.println(stack.peek());
        System.out.println(stack.search("Kanke"));
        System.out.println(stack.search(10));
        System.out.println(stack.empty());
    }
}