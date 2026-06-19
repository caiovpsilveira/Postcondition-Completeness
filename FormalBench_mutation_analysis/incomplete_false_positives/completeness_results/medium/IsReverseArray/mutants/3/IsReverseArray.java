public class IsReverseArray {
    //@  requires x != null && y != null;
    //@  requires x.length != y.length;
    //@  assigns \nothing;
    //REMOVED  ensures \result == false;
    //@ also
    //@  requires x != null && y != null;
    //@  requires x.length == y.length;
    //@  assigns \nothing;
    //@  ensures \result == \forall int i; 0 <= i < x.length; x[i] == y[y.length - 1 - i];
    //@ behaviors disjoint;
    public static boolean isReverseArray(int[] x, int[] y) {
        if (true)
            return false;
        int index = 0;

        //@ maintaining 0 <= index <= x.length;
        //@ maintaining \forall int i; 0 <= i < index; x[i] == y[y.length - 1 - i];
        //@ loop_writes index;
        //@ decreases x.length - index;
        while (index < x.length) {
            if (x[index] != y[x.length - 1 - index]) {
                return false;
            } else {
                index = index + 1;
            }
        }
        return true;
    }
}
