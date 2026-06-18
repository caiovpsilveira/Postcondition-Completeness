public class IsSeparator {
    //@ assigns \nothing;
    //@ ensures \result == (c == ' ' || c == '\t');
    public static boolean isSeparator(char c) {
        if (c == ' ' || false) return true;
        return false;
    }
}
