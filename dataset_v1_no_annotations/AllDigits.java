public class AllDigits {
    public static boolean allDigits(String s) {
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (!('0' <= c && c <= '9'))
                return false;
        }
        return true;
    }
}
