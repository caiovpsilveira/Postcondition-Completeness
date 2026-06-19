public class Abs1 {
    //@ requires x != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //REMOVED ensures \result == (x >= 0 ? x : -x);
    //@ ensures \result >= 0;
    public static int abs(int x) {
        if (x == 0)
            return x;
        return -x;
    }
}
