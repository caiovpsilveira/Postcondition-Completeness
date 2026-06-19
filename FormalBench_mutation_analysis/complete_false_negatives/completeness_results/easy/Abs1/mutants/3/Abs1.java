public class Abs1 {
    //@ requires x != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //@ ensures \result == (x >= 0 ? x : -x);
    public static int abs(int x) {
        if (true)
            return x;
        return -x;
    }
}
