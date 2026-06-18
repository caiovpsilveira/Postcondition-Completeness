public class IsToeplitzMatrix {
    //@ requires mat != null;
    //@ requires \forall int i; 0 <= i < mat.length; mat[i] != null;
    //@ requires \forall int i; 1 <= i < mat.length; mat[i].length == mat[0].length;
    //@ assigns \nothing;
    //@ ensures \result == \forall int i; 1 <= i < mat.length; (\forall int j; 1 <= j < mat[0].length; mat[i][j] == mat[i-1][j-1]);
    public static boolean isToeplitzMatrix(int[][] mat) {
        if (mat.length == 0) return true;
        int n = mat.length, m = mat[0].length;

        //@ maintaining 1 <= i <= n;
        //@ maintaining \forall int p; 1 <= p < i; (\forall int q; 1 <= q < m; mat[p][q] == mat[p-1][q-1]);
        //@ loop_writes i;
        //@ decreases n - i;
        for (int i = 1; i < n; i++) {
            //@ maintaining 1 <= j <= m || j == 1;
            //@ maintaining \forall int q; 1 <= q < j; mat[i][q] == mat[i-1][q-1];
            //@ loop_writes j;
            //@ decreases m - j;
            for (int j = 1; j <= m; j++) {
                if (mat[i][j] != mat[i - 1][j - 1]) {
                    return false;
                }
            }
        }

        return true;
    }
}
