public class TitleCase {
    public static char[] titleCase(char[] arr) {
        if (arr == null) return null;

        int n = arr.length;
        char[] ret = new char[n];

        boolean wordStart = true;
        for (int i = 0; i < n; i++) {
            char c = arr[i];
            if (Character.isWhitespace(c)) {
                ret[i] = c;
                wordStart = true;
            } else if (wordStart) {
                ret[i] = Character.toTitleCase(c);
                wordStart = false;
            } else {
                ret[i] = Character.toLowerCase(c);
            }
        }

        return ret;
    }
}
