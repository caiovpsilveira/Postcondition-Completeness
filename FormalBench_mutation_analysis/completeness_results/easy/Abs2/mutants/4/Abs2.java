public class Abs2 {
    //@ assigns \nothing;
    //@ ensures \result >= 0 && (\result == x || \result == -x);
    public static long abs(int x) {
        long X = (long)x;
        return X >= 0 ? X : +X;
    }
}
