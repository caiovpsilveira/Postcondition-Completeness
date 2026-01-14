public class MatrixSum {
    public static int[][] matrixSum(int[][] a, int[][] b) {
        int n = a.length;
        int m = a[0].length;

        int[][] c = new int[n][m];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                c[i][j] = a[i][j] + b[i][j];
            }
        }

        return c;
    }
}
