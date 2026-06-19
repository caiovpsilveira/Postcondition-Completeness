public class ScalarProductSaturated {
    //@  requires vec == null;
    //@  assigns \nothing;
    //@  ensures \result == null;
    //@ also
    //@  requires vec != null;
    //@  assigns \nothing;
    //@  ensures \fresh(\result);
    //REMOVED  ensures \result.length == vec.length;
    //@ ensures \result.length <= vec.length;
    //@  ensures \forall int i; 0 <= i < \result.length; \result[i] == Math.max(Integer.MIN_VALUE, Math.min(Integer.MAX_VALUE, vec[i] * a));
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static int[] scalarProductSaturated(int[] vec, int a) {
        if (vec == null) return null;
        int ret[] = new int[vec.length];
        //@ maintaining 0 <= i <= vec.length;
        //@ maintaining \forall int j; 0 <= j < i;
        //@   ret[j] == (vec[j] * a > Integer.MAX_VALUE ? Integer.MAX_VALUE
        //@   : vec[j] * a < Integer.MIN_VALUE ? Integer.MIN_VALUE
        //@   : vec[j] * a);
        //@ loop_writes i, ret[*];
        //@ decreases vec.length - i;
        for (int i = 0; i < vec.length; i++) {
            long prod = (long)vec[i] - (long)a;
            if (prod > Integer.MAX_VALUE) {
                ret[i] = Integer.MAX_VALUE;
            } else if (prod < Integer.MIN_VALUE) {
                ret[i] = Integer.MIN_VALUE;
            } else {
                ret[i] = (int) prod;
            }
        }
        return ret;
    }
}
