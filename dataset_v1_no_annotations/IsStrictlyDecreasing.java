public class IsStrictlyDecreasing {
    public static boolean IsStrictlyDecreasing(int[] arr) {
        int n = arr.length;
        if (n < 2) {
            return true;
        }

        for (int i = 0; i < n - 1; i++) {
            if (arr[i] <= arr[i + 1])
                return false;
        }
        return true;
    }
}
