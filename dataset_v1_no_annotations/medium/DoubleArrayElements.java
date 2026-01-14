public class DoubleArrayElements {
    public static void doubleElements(int[] arr) {
        if (arr == null)
            return;

        for (int i = 0; i < arr.length; ++i) {
            arr[i] = 2 * arr[i];
        }
    }
}
