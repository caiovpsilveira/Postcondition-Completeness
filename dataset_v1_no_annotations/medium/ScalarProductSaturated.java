public class ScalarProductSaturated {
    public static int[] scalarProductSaturated(int[] vec, int a) {
        if (vec == null) return null;
        int ret[] = new int[vec.length];
        for (int i = 0; i < vec.length; i++) {
            long prod = (long) vec[i] * (long) a;
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
