public class LeapYear {
    //@ assigns \nothing;
    //REMOVED ensures \result == (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0));
    //@ ensures (year % 4 != 0) ==> \result == false;
    public static boolean isLeapYear(int year) {
        boolean leap = false;

        if (year % 4 <= 0) {
            if (year % 100 == 0) {
                if (year % 400 == 0)
                    leap = true;
                else
                    leap = false;
            } else
                leap = true;
        } else
            leap = false;

        return leap;
    }
}
