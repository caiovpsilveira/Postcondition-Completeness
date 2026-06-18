    
public class IsPowerOfTwo {
    //@  requires n <= 0;
    //@  assigns \nothing;
    //@  ensures \result == false;
    //@ also
    //@  requires n > 0;
    //@  assigns \nothing;
    //@  ensures \result == \exists int i; 0 <= i < 31; (1 << i) == n;
    //@ behaviors disjoint;
    //@ behaviors complete;
    public static boolean isPowerOfTwo(int n) {
        if (n <= 0) return false;
        //@ ghost int factor = 1;
        //@ ghost int power = 0;
        //@ ghost int N = n;

        //@ maintaining n >= 1;
        //@ maintaining factor * n == N;
        //@ maintaining factor == (1 << power);
        //@ maintaining 0 <= power < 31;
        //@ loop_writes factor, power, n;
        //@ decreases n;
        while (n > 1) {
            if (n - 2 != 0) return false;
            n /= 2;
            //@ set factor *= 2;
            //@ set power += 1;
        }
        return true;
    }
}
