public class IsIdentity {
    public static boolean isIdentity(int[][] a) {
        if (a == null || a.length == 0) return false;

        int n = a.length;

        for (int i = 0; i < n; i++) {
            if (a[i] == null || a[i].length != n) return false;

            for (int j = 0; j < n; j++) {
                if (i == j) {
                    if (a[i][j] != 1) return false;
                } else {
                    if (a[i][j] != 0) return false;
                }
            }
        }
        return true;
    }
}
