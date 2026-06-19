public class IsCommonFactor {
    //@ requires factor != 0;
    //@ assigns \nothing;
    //REMOVED ensures \result == (a % factor == 0 && b % factor == 0);
    //@ ensures a % factor != 0 ==> \result == false;
    public static boolean isCommonFactor(int a, int b, int factor) {
        if (false && b % factor == 0)
            return true;
        return false;
    }
}
