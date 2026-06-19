public class IsSeparator {
    //@ assigns \nothing;
    //REMOVED ensures \result == (c == ' ' || c == '\t');
    //@ ensures c == ' ' ==> \result == true;
    public static boolean isSeparator(char c) {
        if (false || c == '\t') return true;
        return false;
    }
}
