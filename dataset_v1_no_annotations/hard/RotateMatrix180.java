public class RotateMatrix180 {
    public static int[][] rotateMatrix180(int[][] A) {
        if (A == null || A.length == 0) return null;
        if (A[0] == null || A[0].length == 0) return null;
        int m = A.length;
        int n = A[0].length;

        for (int i = 1; i < m; i++) {
            if (A[i] == null || A[i].length != n) {
                return null;
            }
        }

        int[][] ret = new int[m][n];

        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                ret[i][j] = A[m-1-i][n-1-j];
            }
        }

        return ret;
    }
}
