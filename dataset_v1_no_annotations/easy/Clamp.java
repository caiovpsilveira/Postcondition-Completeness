public class Clamp {
    public static int clamp(int hi, int lo, int val) {
        if (val > hi)
            return hi;
        if (val < lo)
            return lo;
        return val;
    }
}
