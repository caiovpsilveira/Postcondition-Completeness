public class TitleCase {
    //@  requires arr == null;
    //@  assigns \nothing;
    //@  ensures \result == null;
    //@ also
    //@  requires arr != null;
    //@  assigns \nothing;
    //@  ensures \fresh(\result);
    //@  ensures \result.length == arr.length;
    //@  ensures \forall int i; 0 <= i < arr.length; Character.isWhitespace(arr[i]) ==> \result[i] == arr[i];
    //@  ensures \forall int i; 0 <= i < arr.length; !Character.isWhitespace(arr[i]) && (i == 0 || Character.isWhitespace(arr[i-1])) ==> \result[i] == Character.toTitleCase(arr[i]);
    //@  ensures \forall int i; 0 <= i < arr.length; !(Character.isWhitespace(arr[i]) || (i == 0 || Character.isWhitespace(arr[i-1]))) ==> \result[i] == Character.toLowerCase(arr[i]);
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static char[] titleCase(char[] arr) {
        if (arr == null) return null;

        int n = arr.length;
        char[] ret = new char[n];

        boolean wordStart = true;
        //@ maintaining 0 <= i <= n;
        //@ maintaining wordStart == (i == 0 || Character.isWhitespace(arr[i-1]));
        //@ maintaining \forall int j; 0 <= j < i; Character.isWhitespace(arr[j]) ==> ret[j] == arr[j];
        //@ maintaining \forall int j; 0 <= j < i; !Character.isWhitespace(arr[j]) && (j == 0 || Character.isWhitespace(arr[j-1])) ==> ret[j] == Character.toTitleCase(arr[j]);
        //@ maintaining \forall int j; 0 <= j < i; !(Character.isWhitespace(arr[j]) || (j == 0 || Character.isWhitespace(arr[j-1]))) ==> ret[j] == Character.toLowerCase(arr[j]);
        //@ loop_writes i, wordStart, ret[*];
        //@ decreases n - i;
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
