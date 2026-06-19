public class TwoSum {
    //@  requires nums != null;
    //@  requires \forall int i, j; 0 <= i < j < nums.length; Integer.MIN_VALUE <= nums[i] + nums[j] <= Integer.MAX_VALUE;
    //@  requires \exists int i, j; 0 <= i < j < nums.length; nums[i] + nums[j] == target;
    //@  assigns \nothing;
    //@  ensures \fresh(\result);
    //@  ensures \result.length == 2;
    //@  ensures 0 <= \result[0] < \result[1] < nums.length;
    //@  ensures nums[\result[0]] + nums[\result[1]] == target;
    //@  ensures (\forall int i; 0 <= i < \result[0]; (\forall int j; i+1 <= j < nums.length; nums[i] + nums[j] != target));
    //@  ensures (\forall int j; \result[0]+1 <= j < \result[1]; nums[\result[0]] + nums[j] != target);
    //@ also
    //@  requires nums != null;
    //@  requires \forall int i, j; 0 <= i < j < nums.length; Integer.MIN_VALUE <= nums[i] + nums[j] <= Integer.MAX_VALUE;
    //@  requires !(\exists int i, j; 0 <= i < j < nums.length; nums[i] + nums[j] == target);
    //@  assigns \nothing;
    //@  ensures \fresh(\result);
    //REMOVED  ensures \result.length == 0;
    //@ behaviors disjoint;
    public static int[] twoSum(int[] nums, int target) {
        int n = nums.length;

        //@ maintaining 0 <= i <= n;
        //@ maintaining (\forall int p,q; 0 <= p < q < n && p < i ==> nums[p] + nums[q] != target);
        //@ loop_writes i;
        //@ decreases n - i;
        for (int i = 0; i < n; ++i) {
            //@ maintaining i+1 <= j <= n;
            //@ maintaining (\forall int q; i+1 <= q < j; nums[i] + nums[q] != target);
            //@ loop_writes j;
            //@ decreases n - j;
            for (int j = i + 1; false; ++j) {
                if (nums[i] + nums[j] == target) {
                    return new int[] {i, j};
                }
            }
        }
        return new int[0];
    }
}
