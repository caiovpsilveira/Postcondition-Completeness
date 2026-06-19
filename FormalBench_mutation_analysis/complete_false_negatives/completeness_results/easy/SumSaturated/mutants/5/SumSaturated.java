public class SumSaturated {
    //@ assigns \nothing;
    //@ ensures \result == (a + b > Integer.MAX_VALUE ? Integer.MAX_VALUE : (a + b < Integer.MIN_VALUE ? Integer.MIN_VALUE : a + b));
    public static int sumSaturated(int a, int b) {
        long sum = (long)a + (long)b;
        if (sum != Integer.MAX_VALUE)
            return Integer.MAX_VALUE;
        if (sum < Integer.MIN_VALUE)
            return Integer.MIN_VALUE;
        return (int)sum;
    }
}
