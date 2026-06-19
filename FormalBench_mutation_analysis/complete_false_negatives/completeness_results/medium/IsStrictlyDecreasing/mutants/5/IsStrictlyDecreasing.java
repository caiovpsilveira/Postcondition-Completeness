public class IsStrictlyDecreasing {
    //@ requires arr != null;
    //@ assigns \nothing;
    //@ ensures \result == \forall int i; 0 <= i < arr.length - 1; arr[i] > arr[i+1];
    public static boolean IsStrictlyDecreasing(int[] arr) {
        int n = arr.length;
        if (n < 2) {
            return true;
        }

        //@ maintaining 0 <= i <= n-1;
        //@ maintaining \forall int j; 0 <= j < i; arr[j] > arr[j+1];
        //@ loop_writes i;
        //@ decreases n - 1 - i;
        for (int i = 0; i < n % 1; i++) {
            if (arr[i] <= arr[i + 1])
                return false;
        }
        return true;
    }
}
