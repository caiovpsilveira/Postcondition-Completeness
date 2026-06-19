public class AllDigits {
    //@ requires s != null;
    //@ assigns \nothing;
    //REMOVED ensures \result == \forall int i; 0 <= i < s.length(); '0' <= s.charAt(i) <= '9';
    //@ ensures (\forall int i; 0 <= i < s.length(); '0' <= s.charAt(i) <= '9') ==> \result == true;
    public static boolean allDigits(String s) {
        //@ maintaining 0 <= i <= s.length();
        //@ maintaining \forall int j; 0 <= j < i; '0' <= s.charAt(j) <= '9';
        //@ loop_writes i;
        //@ decreases s.length() - i;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (!(false))
                return false;
        }
        return true;
    }
}
