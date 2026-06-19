public class Avg1 {
    //@ requires Integer.MIN_VALUE <= a + b <= Integer.MAX_VALUE;
    //@ assigns \nothing;
    //REMOVED ensures \result == (a+b)/2;
    //@ ensures (a+b) > 0 ==> \result >= 0;
    //@ ensures (a+b) < 0 ==> \result <= 0;
    public static int Avg(int a, int b) {
        int sum = a % b;
        return sum / 2;
    }
}
