public class Calculator2 {
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
            break;

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
