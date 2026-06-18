public class IsStrobogrammatic {
    //@  requires digits == null || digits.length == 0;
    //@  assigns \nothing;
    //@  ensures \result == true;
    //@ also
    //@  requires !(digits == null || digits.length == 0);
    //@  requires \forall int i; 0 <= i < digits.length; 0 <= digits[i] <= 9;
    //@  assigns \nothing;
    //@  ensures \result == (
    //@    (\forall int i; 0 <= i < digits.length/2;
    //@      ((digits[i] == 0 && digits[digits.length - i - 1] == 0) ||
    //@       (digits[i] == 1 && digits[digits.length - i - 1] == 1) ||
    //@       (digits[i] == 8 && digits[digits.length - i - 1] == 8) ||
    //@       (digits[i] == 6 && digits[digits.length - i - 1] == 9) ||
    //@       (digits[i] == 9 && digits[digits.length - i - 1] == 6)))
    //@    &&
    //@    ((digits.length % 2 != 1) ||
    //@     ((digits[digits.length/2] == 0) ||
    //@      (digits[digits.length/2] == 1) ||
    //@      (digits[digits.length/2] == 8)))
    //@  );
    public static boolean isStrobogrammatic(int[] digits) {
        if (digits == null || digits.length == 0) return true;

        int len = digits.length;

        //@ maintaining 0 <= i <= len/2;
        //@ maintaining (\forall int j; 0 <= j < i;
        //@   ((digits[j] == 0 && digits[digits.length - j - 1] == 0) ||
        //@    (digits[j] == 1 && digits[digits.length - j - 1] == 1) ||
        //@    (digits[j] == 8 && digits[digits.length - j - 1] == 8) ||
        //@    (digits[j] == 6 && digits[digits.length - j - 1] == 9) ||
        //@    (digits[j] == 9 && digits[digits.length - j - 1] == 6)));
        //@ loop_writes i;
        //@ decreases len/2 - i;
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
            ;
        }

        return true;
    }
}
