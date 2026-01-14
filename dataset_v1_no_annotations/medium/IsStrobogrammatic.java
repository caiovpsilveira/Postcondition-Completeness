public class IsStrobogrammatic {
    public static boolean isStrobogrammatic(int[] digits) {
        if (digits == null || digits.length == 0) return true;

        int len = digits.length;

        for (int i = 0; i < len / 2; i++) {
            int a = digits[i];
            int b = digits[len - i - 1];

            if (!((a == 0 && b == 0) ||
                  (a == 1 && b == 1) ||
                  (a == 8 && b == 8) ||
                  (a == 6 && b == 9) ||
                  (a == 9 && b == 6))) {
                return false;
            }
        }

        if ((len % 2) == 1) {
            int mid = digits[len / 2];
            return mid == 0 || mid == 1 || mid == 8;
        }

        return true;
    }
}
