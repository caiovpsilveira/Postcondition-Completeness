public class IsToeplitzMatrix {
    public static boolean isToeplitzMatrix(int[][] mat) {
        if (mat.length == 0) return true;
        int n = mat.length, m = mat[0].length;

        for (int i = 1; i < n; i++) {
            for (int j = 1; j < m; j++) {
                if (mat[i][j] != mat[i - 1][j - 1]) {
                    return false;
                }
            }
        }

        return true;
    }
}
