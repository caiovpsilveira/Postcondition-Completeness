public class RomanNumeralToDec {
    //@  requires N == 'i' || N == 'I' ||
    //@    N == 'v' || N == 'V' ||
    //@    N == 'x' || N == 'X' ||
    //@    N == 'l' || N == 'L' ||
    //@    N == 'c' || N == 'C' ||
    //@    N == 'd' || N == 'D' ||
    //@    N == 'm' || N == 'M';
    //@  assigns \nothing;
    //@  ensures (N == 'i' || N == 'I') ==> \result == 1;
    //@  ensures (N == 'v' || N == 'V') ==> \result == 5;
    //@  ensures (N == 'x' || N == 'X') ==> \result == 10;
    //@  ensures (N == 'l' || N == 'L') ==> \result == 50;
    //@  ensures (N == 'c' || N == 'C') ==> \result == 100;
    //@  ensures (N == 'd' || N == 'D') ==> \result == 500;
    //@  ensures (N == 'm' || N == 'M') ==> \result == 1000;
    //@ also
    //@  requires !(N == 'i' || N == 'I' ||
    //@    N == 'v' || N == 'V' ||
    //@    N == 'x' || N == 'X' ||
    //@    N == 'l' || N == 'L' ||
    //@    N == 'c' || N == 'C' ||
    //@    N == 'd' || N == 'D' ||
    //@    N == 'm' || N == 'M');
    //@  assigns \nothing;
    //REMOVED  ensures \result == -1;
    //@ behaviors disjoint;
    //@ behaviors complete;
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
                ;
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
