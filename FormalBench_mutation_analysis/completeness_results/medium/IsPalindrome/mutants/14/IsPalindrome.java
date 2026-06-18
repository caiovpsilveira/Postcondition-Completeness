public class IsPalindrome {
    //@ requires s != null;
    //@ assigns \nothing;
    //@ ensures \result == (\forall int i; 0 <= i < s.length(); s.charAt(i) == s.charAt(s.length() - 1 - i));
    public static boolean isPalindrome(String s) {
        int n = s.length();

        //@ maintaining 0 <= i <= s.length();
        //@ maintaining \forall int j; 0 <= j < i; s.charAt(j) == s.charAt(s.length() - 1 - j);
        //@ loop_writes i;
        //@ decreases s.length() - i;
        for (int i = 0; i < s.length(); i++) {
            if (true) {
                return false;
            }
        }

        return true;
    }
}
