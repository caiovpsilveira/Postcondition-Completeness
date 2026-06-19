public class Swap2 {
    //@  requires arr != null;
    //@  requires 0 <= a < arr.length && 0 <= b < arr.length;
    //@  assigns arr[a], arr[b];
    //@  ensures arr[a] == \old(arr[b]) && arr[b] == \old(arr[a]);
    public static void swap(int[] arr, int a, int b) {
        int temp = arr[a];
        arr[a] = arr[b];
        arr[b] = temp;
    }
}
