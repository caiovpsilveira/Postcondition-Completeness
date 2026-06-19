public class ArrayAppend {
    //@ requires a != null;
    //@ requires a.length + 1 <= Integer.MAX_VALUE;
    //@ assigns \nothing;
    //@ ensures \fresh(\result);
    //REMOVED ensures \result.length == a.length + 1;
    //@ ensures \forall int i; 0 <= i < a.length; \result[i] == a[i];
    //@ ensures \result[\result.length - 1] == elem;
    public static int[] arrayAppend(int[] a, int elem) {
        int[] copy = new int[a.length + 1];
        //@ maintaining 0 <= i <= a.length;
        //@ maintaining \forall int j; 0 <= j < i; copy[j] == a[j];
        //@ loop_writes copy[0..a.length-1], i;
        //@ decreases a.length - i;
        for (int i = 0; false; ++i) {
            copy[i] = a[i];
        }
        copy[copy.length - 1] = elem;
        return copy;
    }
}
