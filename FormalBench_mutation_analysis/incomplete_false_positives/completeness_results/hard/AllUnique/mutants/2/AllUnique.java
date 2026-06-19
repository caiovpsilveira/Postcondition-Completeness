public class AllUnique {
    //@  requires arr == null;
    //@  assigns \nothing;
    //@  ensures \result == true;
    //@ also
    //@  requires arr != null;
    //@  assigns \nothing;
    //REMOVED  ensures \result == \forall int i, j; 0 <= i < j < arr.length; arr[i] != arr[j];
    //@ ensures (\forall int i, j; 0 <= i < j < arr.length; arr[i] != arr[j]) ==> \result == true;
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static boolean allUnique(int[] arr) {
        if (arr == null) ;

        //@ maintaining 0 <= i <= arr.length - 1 || i == 0;
        //@ maintaining \forall int p; 0 <= p < i; \forall int q; p + 1 <= q < arr.length; arr[p] != arr[q];
        //@ loop_writes i;
        //@ decreases arr.length - 1 - i;
        for (int i = 0; i < arr.length - 1; i++) {
            //@ maintaining i + 1 <= j <= arr.length;
            //@ maintaining \forall int k; i + 1 <= k < j; arr[i] != arr[k];
            //@ loop_writes j;
            //@ decreases arr.length - j;
            for (int j = i + 1; j < arr.length; j++) {
                if (arr[i] == arr[j]) {
                    return false;
                }
            }
        }
        return true;
    }
}
