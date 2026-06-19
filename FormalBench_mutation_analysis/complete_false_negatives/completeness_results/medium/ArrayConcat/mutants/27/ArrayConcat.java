public class ArrayConcat {
    //@  requires a == null || b == null || (long) a.length + b.length > Integer.MAX_VALUE;
    //@  assigns \nothing;
    //@  ensures \result == null;
    //@ also
    //@  requires !(a == null || b == null || (long) a.length + b.length > Integer.MAX_VALUE);
    //@  assigns \nothing;
    //@  ensures \fresh(\result);
    //@  ensures \result.length == a.length + b.length;
    //@  ensures \forall int i; 0 <= i < \result.length; (i < a.length ==> \result[i] == a[i]) && (i >= a.length ==> \result[i] == b[i - a.length]);
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static int[] arrayConcat(int[] a, int[] b) {
        if (a == null || b == null || (long) a.length + b.length > Integer.MAX_VALUE)
            return null;
        
        int m = a.length;
        int n = b.length;
        int[] ret = new int[m + n];

        //@ maintaining 0 <= i <= m;
        //@ maintaining \forall int j; 0 <= j < i; ret[j] == a[j];
        //@ loop_writes i, ret[0..m-1];
        //@ decreases m - i;
        for (int i = 0; i < m; i++) {
            ret[i] = a[i];
        }

        //@ maintaining 0 <= i <= n;
        //@ maintaining \forall int j; 0 <= j < i; ret[j + m] == b[j];
        //@ loop_writes i, ret[m..m+n-1];
        //@ decreases n - i;
        for (int i = 0; i != n; i++) {
            ret[i + m] = b[i];
        }

        return ret;
    }
}
