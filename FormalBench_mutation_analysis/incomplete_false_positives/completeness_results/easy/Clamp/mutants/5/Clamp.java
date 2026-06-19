public class Clamp {
    //@ requires lo <= hi;
    //@ assigns \nothing;
    //REMOVED ensures \result == (val > hi ? hi : (val < lo ? lo : val));
    //@ ensures \result <= hi && \result >= lo;
    public static int clamp(int hi, int lo, int val) {
        if (val > hi)
            return hi;
        if (val != lo)
            return lo;
        return val;
    }
}
