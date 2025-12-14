public class Avg2 {
    //@ assigns \nothing;
    //@ ensures \result == (a+b)/2;
    public static int Avg(int a, int b) {
        long sum = (long)a + (long)b;
        return (int)(sum / 2);
    }
}
