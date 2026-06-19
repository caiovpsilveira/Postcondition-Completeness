public class DoubleArrayElements {
    //@  requires arr == null;
    //@  assigns \nothing;
    //@ also
    //@  requires arr != null;
    //@  requires \forall int i; 0 <= i < arr.length; Integer.MIN_VALUE <= 2 * arr[i] <= Integer.MAX_VALUE;
    //@  assigns arr[*];
    //REMOVED  ensures \forall int i; 0 <= i < arr.length; arr[i] == 2 * \old(arr[i]);
    //@ ensures \forall int i; 0 <= i < arr.length; \old(arr[i]) > 0 ==> (arr[i] == 2 * \old(arr[i]));
    //@ behaviors disjoint;
    public static void doubleElements(int[] arr) {
        if (arr == null)
            return;

        //@ maintaining 0 <= i <= arr.length;
        //@ maintaining \forall int j; 0 <= j < i; arr[j] == 2 * \old(arr[j]);
        //@ maintaining \forall int j; i <= j < arr.length; arr[j] == \old(arr[j]);
        //@ loop_writes arr[*], i;
        //@ decreases arr.length - i;
        for (int i = 0; i < arr.length; ++i) {
            ;
        }
    }
}
