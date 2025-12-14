public class SafeSum {
    public static int safeSum(int a, int b) {
        long sum = (long)a + (long)b;
        if (sum > Integer.MAX_VALUE)
            return Integer.MAX_VALUE;
        if (sum < Integer.MIN_VALUE)
            return Integer.MIN_VALUE;
        return (int)sum;
    }
}