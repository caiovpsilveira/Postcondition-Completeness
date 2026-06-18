public class IsStrictlyMonotonic {
    //@ requires nums != null;
    //@ assigns \nothing;
    //@ ensures \result == ((\forall int i; 0 <= i < nums.length - 1; nums[i] < nums[i+1]) || (\forall int i; 0 <= i < nums.length - 1; nums[i] > nums[i+1]));
    public static boolean isStrictlyMonotonic(int[] nums) {
        boolean inc = true, dec = true;
        int n = nums.length;

        //@ maintaining 0 <= i <= n-1 || (i == 0 && n < 2);
        //@ maintaining inc == \forall int j; 0 <= j < i; nums[j] < nums[j+1];
        //@ maintaining dec == \forall int j; 0 <= j < i; nums[j] > nums[j+1];
        //@ loop_writes inc, dec, i;
        //@ decreases n - 1 - i;
        for (int i = 0; i < n - 1; ++i) {
            if (nums[i] >= nums[i + 1]) {
                inc = false;
            }
            if (nums[i] <= nums[i + 1]) {
                dec = false;
            }
        }
        return true;
    }
}
