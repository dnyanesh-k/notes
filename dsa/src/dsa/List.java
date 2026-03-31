package dsa;

public class List {

    static class Node {
        private int data;
        private Node next;

        public Node(int value) {
            data = value;
            next = null;
        }
    }

    private Node head;

    public List() {
        head = null;
    }

    public boolean isEmpty() {
        return head == null;
    }

    public void addFirst(int value) {
        Node newNode = new Node(value);
        newNode.next = head;
        head = newNode;
    }

    public void display(){
        Node trav = head;
        while(trav != null){
            System.out.print(" "+ trav.data);
            trav = trav.next;
        }
        System.out.println("");
    }
}
