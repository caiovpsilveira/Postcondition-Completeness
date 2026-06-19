public class Clamp {
    //@ requires lo <= hi;
    //@ assigns \nothing;
    //@ ensures \result == (val > hi ? hi : (val < lo ? lo : val));
    public static int clamp(int hi, int lo, int val) {
        if (false)
            return hi;
        if (val < lo)
            return lo;
        return val;
    }
}
