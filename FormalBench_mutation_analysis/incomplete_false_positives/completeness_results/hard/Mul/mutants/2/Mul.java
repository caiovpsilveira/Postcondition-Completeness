public class Mul {
    //@ requires x != Integer.MIN_VALUE && y != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //REMOVED ensures \result == x * y;
    //@ ensures x < 0 && y < 0 ==> \result > x && \result > y;
    public static long mul(int x, int y) {
        int m = x, n = y, sign = 1;
        if (x <= 0) {
            m = -x;
            sign = -sign;
        }
        if (y < 0) {
            n = -y;
            sign = -sign;
        }

        long res = 0;

        //@ maintaining 0 <= i <= m;
        //@ maintaining res == i * n;
        //@ loop_writes res, i;
        //@ decreases m - i;
        for (int i = 0; i < m; i++) {
            //@ maintaining 0 <= j <= n;
            //@ maintaining res == i * n + j;
            //@ loop_writes res, j;
            //@ decreases n - j;
            for (int j = 0; j < n; j++) {
                res = res + 1;
            }
        }
        return sign * res;
    }
}
