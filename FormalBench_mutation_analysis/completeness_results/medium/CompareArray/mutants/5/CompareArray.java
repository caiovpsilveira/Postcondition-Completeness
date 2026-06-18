public class CompareArray {
    //@  requires a == null || b == null;
    //@  assigns \nothing;
    //@  ensures \result == (a == b);
    //@ also
    //@  requires a != null && b != null;
    //@  assigns \nothing;
    //@  ensures \result == (a.length == b.length && \forall int i; 0 <= i < a.length; a[i] == b[i]);
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static boolean arrcmp(int[] a, int[] b) {
        if (b == null) {
            return a == b;
        }
        if (a.length != b.length) {
            return false;
        }

        //@ maintaining 0 <= i <= a.length;
        //@ maintaining \forall int j; 0 <= j < i; a[j] == b[j];
        //@ loop_writes i;
        //@ decreases a.length - i;
        for (int i = 0; i < a.length; i++) {
            if (a[i] != b[i]) {
                return false;
            }
        }

        return true;
    }
}
