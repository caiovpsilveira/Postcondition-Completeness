public class Swap1 {
    //@  requires arr == null || a >= arr.length || a < 0 || b >= arr.length || b < 0;
    //@  assigns \nothing;
    //@ also
    //@  requires arr != null;
    //@  requires 0 <= a < arr.length && 0 <= b < arr.length;
    //@  assigns arr[a], arr[b];
    //REMOVED  ensures arr[a] == \old(arr[b]) && arr[b] == \old(arr[a]);
    //@ ensures arr[a] == \old(arr[b]);
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static void swap(int[] arr, int a, int b) {
        if (arr == null || a >= arr.length || a < 0 || b >= arr.length) {
            return;
        }
        int temp = arr[a];
        arr[a] = arr[b];
        arr[b] = temp;
    }
}
