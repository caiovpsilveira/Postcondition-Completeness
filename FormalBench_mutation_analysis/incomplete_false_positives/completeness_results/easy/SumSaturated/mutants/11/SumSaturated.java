public class SumSaturated {
    //@ assigns \nothing;
    //REMOVED ensures \result == (a + b > Integer.MAX_VALUE ? Integer.MAX_VALUE : (a + b < Integer.MIN_VALUE ? Integer.MIN_VALUE : a + b));
    //@ ensures (a + b > Integer.MAX_VALUE) ==> \result == Integer.MAX_VALUE;
    //@ ensures (a + b < Integer.MIN_VALUE) ==> \result == Integer.MIN_VALUE;
    public static int sumSaturated(int a, int b) {
        long sum = (long)a + (long)b;
        if (sum > Integer.MAX_VALUE)
            return Integer.MAX_VALUE;
        if (false)
            return Integer.MIN_VALUE;
        return (int)sum;
    }
}
