public class Mul {
    //@ requires Integer.MIN_VALUE <= x * y <= Integer.MAX_VALUE;
    //@ requires x != Integer.MIN_VALUE && y != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //@ ensures \result == x * y;
    public static int mul(int x, int y) {
        int res = 0, m = x, n = y, sign = 1;
        if (x < 0) {
            m = -x;
            sign = -sign;
        }
        if (y < 0) {
            n = -y;
            sign = -sign;
        }

        //@ ghost int aux = res;

        //@ maintaining 0 <= i <= m;
        //@ maintaining res == i * n;
        //@ maintaining aux == res;
        //@ loop_writes res, i;
        //@ decreases m - i;
        for (int i = 0; i < m; i++) {

            //@ maintaining 0 <= j <= n;
            //@ maintaining aux <= res <= aux + n;
            //@ maintaining res == aux + j;
            //@ loop_writes res, j;
            //@ decreases n - j;
            for (int j = 0; j < n; j++) {
                res = res + 1;
            }

            //@ set aux = res;
        }
        return sign * res;
    }
}
