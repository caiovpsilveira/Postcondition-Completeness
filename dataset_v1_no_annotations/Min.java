public class Min {
    public static int min(int[] a) {
        int res = a[0];

        for (int i = 1; i < a.length; i++) {
            res = ((a[i] < res) ? a[i] : res);
        }
        return res;
    }
}
