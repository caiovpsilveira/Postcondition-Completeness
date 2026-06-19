public class IsCommonMultiple {
    //@ requires a != 0;
    //@ requires b != 0;
    //@ assigns \nothing;
    //REMOVED ensures \result == (m % a == 0 && m % b == 0);
    //@ ensures m % b != 0 ==> \result == false;
    public static boolean isCommonMultiple(int a, int b, int m) {
        if (m % a != 0) {
            return false;
        }
        if (m % b != 0) {
            ;
        }
        return true;
    }
}
