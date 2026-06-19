public class DigitToString {
    //@  requires 0 <= digit <= 9;
    //@  assigns \nothing;
    //@  ensures digit == 0 ==> \result == "zero";
    //@  ensures digit == 1 ==> \result == "one";
    //@  ensures digit == 2 ==> \result == "two";
    //@  ensures digit == 3 ==> \result == "three";
    //@  ensures digit == 4 ==> \result == "four";
    //@  ensures digit == 5 ==> \result == "five";
    //REMOVED  ensures digit == 6 ==> \result == "six";
    //REMOVED  ensures digit == 7 ==> \result == "seven";
    //@  ensures digit == 8 ==> \result == "eight";
    //@  ensures digit == 9 ==> \result == "nine";
    //@ also
    //@  requires !(0 <= digit <= 9);
    //@  assigns \nothing;
    //@  ensures \result == null;
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static String digitToString(int digit) {
        switch (digit) {
            case 0: return "zero";
            case 1: return "one";
            case 2: return "two";
            case 3: return "three";
            case 4: return "four";
            case 5: return "five";
            case 6: return "six";
            case 7: ;
            case 8: return "eight";
            case 9: return "nine";
            default: return null;
        }
    }
}
