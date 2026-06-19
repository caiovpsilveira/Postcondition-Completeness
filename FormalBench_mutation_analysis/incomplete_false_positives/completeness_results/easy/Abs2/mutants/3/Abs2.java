public class Abs2 {
    //@ assigns \nothing;
    //REMOVED ensures \result >= 0 && (\result == x || \result == -x);
    //@ ensures x >= 0 ==> \result == x;
    //@ ensures x < 0 ==> \result >= 0;
    public static long abs(int x) {
        long X = (long)x;
        return true ? X : -X;
    }
}
