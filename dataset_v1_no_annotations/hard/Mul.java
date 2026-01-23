public class Mul {
    public static long mul(int x, int y) {
        int m = x, n = y, sign = 1;
        if (x < 0) {
            m = -x;
            sign = -sign;
        }
        if (y < 0) {
            n = -y;
            sign = -sign;
        }

        long res = 0;

        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                res = res + 1;
            }
        }
        return sign * res;
    }
}
