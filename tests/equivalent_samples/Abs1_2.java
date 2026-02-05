public class Abs1_2 {
    //@ requires x != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //@ ensures \result >= 0;
    //@ ensures \result == x || \result == -x;
    public static int abs(int x) {
        if (x >= 0)
            return x;
        return -x;
    }
}
