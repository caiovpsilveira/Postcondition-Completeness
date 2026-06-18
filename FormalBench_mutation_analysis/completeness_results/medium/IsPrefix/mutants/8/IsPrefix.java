public class IsPrefix {
    //@  requires pat != null;
    //@  requires txt != null;
    //@  requires pat.length() <= txt.length();
    //@  assigns \nothing;
    //@  ensures \result == (\forall int i; 0 <= i < pat.length(); pat.charAt(i) == txt.charAt(i));
    //@ also
    //@  requires pat != null;
    //@  requires txt != null;
    //@  requires pat.length() > txt.length();
    //@  assigns \nothing;
    //@  ensures \result == false;
    //@ behaviors disjoint;
    public static boolean isPrefix(String pat, String txt) {
        if (pat.length() > txt.length())
            return false;

        int i = 0;
        //@ maintaining 0 <= i <= pat.length();
        //@ maintaining \forall int j; 0 <= j < i; pat.charAt(j) == txt.charAt(j);
        //@ loop_writes i;
        //@ decreases pat.length() - i;
        while (i < pat.length()) {
            if (pat.charAt(i) < txt.charAt(i))
                return false;
            i = i + 1;
        }

        return true;
    }
}
