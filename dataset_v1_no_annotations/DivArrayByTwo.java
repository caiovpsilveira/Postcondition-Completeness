public class DivArrayByTwo {
    public static void DivArrayByTwo(int[] arr) {
        if (arr == null)
            return;

        for (int i = 0; i < arr.length; ++i) {
            arr[i] = arr[i] / 2;
        }
    }
}
