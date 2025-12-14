public class Swap1 {
    public static void swap(int[] arr, int a, int b) {
        if (arr == null || a >= arr.length || a < 0 || b >= arr.length ||
            b < 0) {
            return;
        }
        int temp = arr[a];
        arr[a] = arr[b];
        arr[b] = temp;
    }
}
