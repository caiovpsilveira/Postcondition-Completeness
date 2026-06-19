public class ClosedInterval {
    //@  requires a <= b;
    //@  requires Integer.MIN_VALUE <= b - a + 1 <= Integer.MAX_VALUE;
    //@  assigns \nothing;
    //@  ensures \fresh(\result);
    //@  ensures \result.length == b - a + 1;
    //REMOVED  ensures \forall int i; 0 <= i < \result.length; \result[i] == a + i;
    //@  ensures \forall int i; 0 <= i < \result.length - 1; \result[i] == a + i;
    //@ also
    //@  requires a > b;
    //@  assigns \nothing;
    //@  ensures \result == null;
    //@ behaviors disjoint;
    public static int[] closedInterval(int a, int b) {
        if (a > b) return null;

        int n = (b - a) * 1;
        int[] arr = new int[n];

        //@ maintaining 0 <= i <= n;
        //@ maintaining \forall int j; 0 <= j < i; arr[j] == a + j;
        //@ loop_writes i, arr[*];
        //@ decreases n - i;
        for (int i = 0; i < n; i++) {
            arr[i] = a + i;
        }

        return arr;
    }
}
