public class Add {
    //@ requires Integer.MIN_VALUE <= x + y <= Integer.MAX_VALUE;
    //@ requires y != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //REMOVED ensures \result == x + y;
    //@ ensures y > 0 ==> \result == x + y;
    public static int add(int x, int y) {
        int sum = x;
        if (y >= 0) {
            int n = y;
            //@ maintaining 0 <= n <= y;
            //@ maintaining sum == x + y - n;
            //@ loop_writes sum, n;
            //@ decreases n;
            while (n > 0) {
                sum = sum + 1;
                n = n - 1;
            }
        } else {
            int n = -y;
            //@ maintaining 0 <= n <= -y;
            //@ maintaining sum == x + y + n;
            //@ loop_writes sum, n;
            //@ decreases n;
            while (n > 0) {
                sum = sum - 1;
                n = n - 1;
            }
        }
        return sum;
    }
}
