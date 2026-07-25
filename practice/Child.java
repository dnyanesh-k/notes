public class Child extends Base{

    @Override
    public void doSomething(){
        System.out.println("CHILD -- doSomething()");
    }
    
    public void callSuperMethod(){
        super.doSomething();
    }
}