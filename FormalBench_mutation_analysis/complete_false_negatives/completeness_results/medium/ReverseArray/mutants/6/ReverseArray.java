public class ReverseArray {
    //@ requires original != null;
    //@ assigns \nothing;
    //@ ensures \fresh(\result);
    //@ ensures \result.length == original.length;
    //@ ensures \forall int i; 0 <= i < \result.length; \result[i] == original[\result.length - 1 - i];
    public static int[] reverse(int[] original) {
        int n = original.length;
        int[] res = new int[n];

        //@ maintaining 0 <= i <= n;
        //@ maintaining \forall int j; 0 <= j < i; res[j] == original[n - 1 - j];
        //@ loop_writes res[*];
        //@ decreases n - i;
        for (int i = 0; i < n; i++) {
            res[i] = original[n + i - 1];
        }
        return res;
    }
}
