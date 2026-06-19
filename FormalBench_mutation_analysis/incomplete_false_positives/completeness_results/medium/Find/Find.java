public class Find {
    //@  requires arr != null;
    //@  requires \exists int i; 0 <= i < arr.length; arr[i] == elem;
    //@  assigns \nothing;
    //@  ensures 0 <= \result < arr.length;
    //REMOVED  ensures \forall int i; 0 <= i < \result; arr[i] != elem;
    //@  ensures arr[\result] == elem;
    //@ also
    //@  requires arr == null || \forall int i; 0 <= i < arr.length; arr[i] != elem;
    //@  assigns \nothing;
    //@  ensures \result == -1;
    //@ behaviors disjoint;
    //@ behaviors complete;
    //@ pure
    public static int find(int[] arr, int elem) {
        if (arr == null)
            return -1;
        //@ maintaining 0 <= i <= arr.length;
        //@ maintaining \forall int j; 0 <= j < i; arr[j] != elem;
        //@ loop_writes i;
        //@ decreases arr.length - i;
        for (int i = 0; i < arr.length; i++)
            if (arr[i] == elem)
                return i;
        return -1;
    }
}
