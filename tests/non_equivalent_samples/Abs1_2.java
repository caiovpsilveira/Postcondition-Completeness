public class Abs1_2 {
    //@ requires x >= -100;
    //@ assigns \nothing;
    //@ ensures \result == (x >= 0 ? x : -x);
    public static int abs(int x) {
        if (x >= 0)
            return x;
        return -x;
    }
}
