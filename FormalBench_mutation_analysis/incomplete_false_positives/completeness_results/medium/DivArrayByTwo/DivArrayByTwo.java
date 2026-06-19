public class DivArrayByTwo {
    //@  requires arr == null;
    //@  assigns \nothing;
    //@ also
    //@  requires arr != null;
    //@  assigns arr[*];
    //REMOVED  ensures \forall int i; 0 <= i < arr.length; arr[i] == \old(arr[i]) / 2;
    //@ ensures \forall int i; 0 <= i < arr.length; (\old(arr[i]) >= 0) ==> (arr[i] <= \old(arr[i]));
    //@ ensures \forall int i; 0 <= i < arr.length; (\old(arr[i]) < 0) ==> (arr[i] >= \old(arr[i]));
    //@ behaviors complete;
    //@ behaviors disjoint;
    public static void DivArrayByTwo(int[] arr) {
        if (arr == null)
            return;

        //@ maintaining 0 <= i <= arr.length;
        //@ maintaining \forall int j; 0 <= j < i; arr[j] == \old(arr[j]) / 2;
        //@ maintaining \forall int k; i <= k < arr.length; arr[k] == \old(arr[k]);
        //@ loop_writes arr[*], i;
        //@ decreases arr.length - i;
        for (int i = 0; i < arr.length; ++i) {
            arr[i] = arr[i] / 2;
        }
    }
}
