import java.util.*;

class HelloWorld{
    public static void main(String [] args){
        // System.out.println("Hello World");
        // if (args.length > 0){
        // System.out.println("Arg 1 : " + args[0]);
        // System.out.println("Arg 2 : " + args[1]);
        // }
    Scanner sc = new Scanner(System.in);
    System.out.println("Enter Name: ");
    String name = sc.nextLine();
    System.out.println("Enter Age : ");
    int age = sc.nextInt();
    System.out.println("Name : " + name + "\nAge : " + age);
    
    Demo d = new Demo();
    d.info();
    }
}