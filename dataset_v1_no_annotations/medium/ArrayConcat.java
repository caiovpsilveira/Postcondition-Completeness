public class ArrayConcat {
    public static int[] arrayConcat(int[] a, int[] b) {
        if (a == null || b == null || (long) a.length + b.length > Integer.MAX_VALUE)
            return null;
        
        int m = a.length;
        int n = b.length;
        int[] ret = new int[m + n];

        for (int i = 0; i < m; i++) {
            ret[i] = a[i];
        }

        for (int i = 0; i < n; i++) {
            ret[i + m] = b[i];
        }

        return ret;
    }
}
