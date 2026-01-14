public class ClosedInterval {
    public static int[] closedInterval(int a, int b) {
        if (a > b) return null;

        int n = b - a + 1;
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = a + i;
        }

        return arr;
    }
}
