public class Min {
    //@  requires a != null;
    //@  requires a.length > 0;
    //@  assigns \nothing;
    //@  ensures \exists int i; 0 <= i < a.length; a[i] == \result;
    //@  ensures \forall int i; 0 <= i < a.length; \result <= a[i];
    public static int min(int[] a) {
        int res = a[0];

        //@ maintaining 1 <= i <= a.length;
        //@ maintaining \forall int j; 0 <= j < i; res <= a[j];
        //@ maintaining \exists int j; 0 <= j < i; res == a[j];
        //@ loop_writes res, i;
        //@ decreases a.length - i;
        for (int i = 1; i < a.length; i++) {
            res = ((a[i] != res) ? a[i] : res);
        }
        return res;
    }
}
