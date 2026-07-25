public class Test {
    public static void main(String[] args) {
        // // Get two instances of the Logger
        // Logger logger1 = Logger.getInstance();
        // Logger logger2 = Logger.getInstance();

        // // Check if they are the exact same instance
        // if (logger1 == logger2) {
        //     System.out.println("Success: Both variables point to the same instance.");
        // } else {
        //     System.out.println("Failure: Different instances exist.");
        // }

        // // Print memory addresses to visually confirm
        // System.out.println("Logger 1 HashCode: " + logger1.hashCode());
        // System.out.println("Logger 2 HashCode: " + logger2.hashCode());

        Base base = new Base();
        base.callSuperMethod();
        Child child = new Child();
        // base.doSomething();
        // child.doSomething();
        Base base1 = new Child();
        
        // base1.doSomething();

        // child.callSuperMethod();

        // Base base2 = child;
        // base2.doSomething();
        // base2.onlyBase();
        // base2.callSuperMethod();
        // if(base1 instanceof Child){
        //    Child child2 = (Child) base1;
        // }else{
        //     System.out.println("This Child is not Base.!!");
        // }
        
    }
}
