public class AllDigits {
    //@ requires s != null;
    //@ assigns \nothing;
    //@ ensures \result == \forall int i; 0 <= i < s.length(); '0' <= s.charAt(i) <= '9';
    public static boolean allDigits(String s) {
        //@ maintaining 0 <= i <= s.length();
        //@ maintaining \forall int j; 0 <= j < i; '0' <= s.charAt(j) <= '9';
        //@ loop_writes i;
        //@ decreases s.length() - i;
        for (int i = 0; i != s.length(); i++) {
            char c = s.charAt(i);
            if (!('0' <= c && c <= '9'))
                return false;
        }
        return true;
    }
}
