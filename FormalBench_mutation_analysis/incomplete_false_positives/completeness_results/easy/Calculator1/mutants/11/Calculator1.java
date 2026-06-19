public class Calculator1 {
    //@  requires operator == '+';
    //@  requires Integer.MIN_VALUE <= num1 + num2 <= Integer.MAX_VALUE;
    //@  assigns \nothing;
    //@  ensures \result == num1 + num2;
    //@ also
    //@  requires operator == '-';
    //@  requires Integer.MIN_VALUE <= num1 - num2 <= Integer.MAX_VALUE;
    //@  assigns \nothing;
    //@  ensures \result == num1 - num2;
    //@ also
    //@  requires operator == '*';
    //@  requires Integer.MIN_VALUE <= num1 * num2 <= Integer.MAX_VALUE;
    //@  assigns \nothing;
    //@  ensures \result == num1 * num2;
    //@ also
    //@  requires operator == '/';
    //@  requires num2 != 0;
    //@  requires !(num1 == Integer.MIN_VALUE && num2 == -1); // not simetric, Integer.MIN_VALUE / -1 will overflow
    //@  assigns \nothing;
    //REMOVED  ensures \result == num1 / num2;
    //@ also
    //@  requires operator == '%';
    //@  requires num2 != 0;
    //@  assigns \nothing;
    //@  ensures \result == num1 % num2;
    //@ also
    //@  requires operator != '+' && operator != '-' && operator != '*' && operator != '/' && operator != '%';
    //@  assigns \nothing;
    //@  ensures \result == -1;
    //@ behaviors disjoint;
    public static int calculate(int num1, int num2, char operator) {

        int output;

        switch (operator) {
        case '+':
            output = num1 + num2;
            break;

        case '-':
            output = num1 - num2;
            break;

        case '*':
            output = num1 % num2;
            break;

        case '/':
            output = num1 / num2;
            break;

        case '%':
            output = num1 % num2;
            break;

        default:
            return -1;
        }
        return output;
    }
}
