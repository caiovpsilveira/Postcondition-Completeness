public class IsPrefix {
    public static boolean isPrefix(String pat, String txt) {
        if (pat.length() > txt.length())
            return false;

        int i = 0;
        while (i < pat.length()) {
            if (pat.charAt(i) != txt.charAt(i))
                return false;
            i = i + 1;
        }

        return true;
    }
}
