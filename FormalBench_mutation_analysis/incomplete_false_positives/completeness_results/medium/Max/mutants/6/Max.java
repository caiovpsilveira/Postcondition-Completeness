public class Max {
    //@  requires a == null || a.length == 0;
    //@  assigns \nothing;
    //@  ensures \result == Integer.MIN_VALUE;
    //@ also
    //@  requires a != null;
    //@  requires a.length > 0;
    //@  assigns \nothing;
    //REMOVED  ensures \exists int i; 0 <= i < a.length; a[i] == \result;
    //@  ensures \forall int i; 0 <= i < a.length; \result >= a[i];
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static int max(int[] a) {
        if (a.length == 0)
            return Integer.MIN_VALUE;
        int res = a[0];

        //@ maintaining 1 <= i <= a.length;
        //@ maintaining \forall int j; 0 <= j < i; res >= a[j];
        //@ maintaining \exists int j; 0 <= j < i; res == a[j];
        //@ loop_writes res, i;
        //@ decreases a.length - i;
        for (int i = 1; i < a.length; i++) {
            res = ((a[i] > res) ? a[i] : res);
        }
        return res;
    }
}
