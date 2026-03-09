public class Calc {
    //@  requires op == '+' || op == '-';
    //@  requires Integer.MIN_VALUE <= a + b <= Integer.MAX_VALUE;
    //@  requires Integer.MIN_VALUE <= a - b <= Integer.MAX_VALUE;
    //@  assigns \nothing;
    //@  ensures \result == a + b || \result == a - b;
    public static int calc(int a, int b, char op) {
        if (op == '+') {
            return a + b;
        } else if (op == '-') {
            return a - b;
        }
    }
}
