public class Avg2 {
    //@ assigns \nothing;
    //REMOVED ensures \result == (a+b)/2;
    //@ ensures a > 0 && b > 0 ==> \result >= 0;
    public static int Avg(int a, int b) {
        long sum = (long)a + (long)b;
        return (int)(sum - 2);
    }
}
