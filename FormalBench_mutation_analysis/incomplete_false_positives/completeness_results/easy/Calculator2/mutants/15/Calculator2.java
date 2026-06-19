public class Calculator2 {
    //@  requires operator == '+';
    //@  assigns \nothing;
    //@  ensures \result == num1 + num2;
    //@ also
    //@  requires operator == '-';
    //@  assigns \nothing;
    //REMOVED  ensures \result == num1 - num2;
    //@ also
    //@  requires operator == '*';
    //@  assigns \nothing;
    //@  ensures \result == num1 * num2;
    //@ also
    //@  requires operator == '/';
    //@  requires num2 != 0;
    //@  assigns \nothing;
    //@  ensures \result == num1 / num2;
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
    public static long calculate(int num1, int num2, char operator) {

        long output;

        switch (operator) {
        case '+':
            output = (long)num1 + num2;
            break;

        case '-':
            output = (long)num1 - num2;
            break;

        case '*':
            output = (long)num1 * num2;
            ;

        case '/':
            output = (long)num1 / num2;
            break;

        case '%':
            output = (long)num1 % num2;
            break;

        default:
            return -1;
        }
        return output;
    }
}
