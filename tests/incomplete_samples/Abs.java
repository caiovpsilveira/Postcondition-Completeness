public class Abs {
    //@ requires x != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //@ ensures \result >= 0;
    //REMOVED@ ensures (\result == x) || (\result == -x);
    public static int abs(int x) {
        if (x < 0) {
            return -x;
        } else {
            return x;
        }
    }
}
