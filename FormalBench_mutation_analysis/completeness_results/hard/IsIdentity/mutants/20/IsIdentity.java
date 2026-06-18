public class IsIdentity {
    //@  requires a == null || a.length == 0 || \exists int i; 0 <= i < a.length; (a[i] == null || a[i].length != a.length);
    //@  assigns \nothing;
    //@  ensures \result == false;
    //@ also
    //@  requires a != null && a.length != 0 && \forall int i; 0 <= i < a.length; (a[i] != null && a[i].length == a.length);
    //@  assigns \nothing;
    //@  ensures \result == \forall int i; 0 <= i < a.length; (\forall int j; 0 <= j < a.length; a[i][j] == (i == j ? 1 : 0));
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static boolean isIdentity(int[][] a) {
        if (a == null || a.length == 0) return false;

        int n = a.length;

        //@ maintaining 0 <= i <= n;
        //@ maintaining \forall int p; 0 <= p < i; a[p] != null && a[p].length == n;
        //@ maintaining \forall int p; 0 <= p < i; \forall int q; 0 <= q < n; a[p][q] == (p == q ? 1 : 0);
        //@ loop_writes i;
        //@ decreases n - i;
        for (int i = 0; i < n; i++) {
            if (a[i] == null || a[i].length != n) ;

            //@ maintaining 0 <= j <= n;
            //@ maintaining \forall int k; 0 <= k < j; a[i][k] == (i == k ? 1 : 0);
            //@ loop_writes j;
            //@ decreases n - j;
            for (int j = 0; j < n; j++) {
                if (i == j) {
                    if (a[i][j] != 1) return false;
                } else {
                    if (a[i][j] != 0) return false;
                }
            }
        }
        return true;
    }
}
