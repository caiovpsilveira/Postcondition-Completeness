public class RomanNumeralToDec {
    public static int romanNumeralToDec(char N) {
        switch (N) {
            case 'i':
            case 'I':
                return 1;
            case 'v':
            case 'V':
                return 5;
            case 'x':
            case 'X':
                return 10;
            case 'l':
            case 'L':
                return 50;
            case 'c':
            case 'C':
                return 100;
            case 'd':
            case 'D':
                return 500;
            case 'm':
            case 'M':
                return 1000;
        }
        return -1;
    }
}
