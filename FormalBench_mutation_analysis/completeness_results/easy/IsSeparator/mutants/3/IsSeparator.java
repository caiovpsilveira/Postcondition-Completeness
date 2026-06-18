public class IsSeparator {
    //@ assigns \nothing;
    //@ ensures \result == (c == ' ' || c == '\t');
    public static boolean isSeparator(char c) {
        if (false || c == '\t') return true;
        return false;
    }
}
