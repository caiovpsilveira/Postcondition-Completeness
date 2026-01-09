public class IdxMaximum {
    //@  requires a != null;
    //@  requires a.length > 0;
    //@  assigns \nothing;
    //@  ensures 0 <= \result < a.length;
    //@  ensures \forall int i; 0 <= i < \result; a[\result] > a[i];
    //@  ensures \forall int i; \result <= i < a.length; a[\result] >= a[i];
    //@ also
    //@  requires a != null;
    //@  requires a.length == 0;
    //@  assigns \nothing;
    //@  ensures \result == -1;
    //@ behaviors disjoint;
    public static int idxMaximum(int[] a) {
        if (a.length == 0)
            return -1;

        int index = 0;
        int biggest = 0;

        //@ maintaining 0 <= index <= a.length;
        //@ maintaining 0 <= biggest < a.length;
        //@ maintaining \forall int i; 0 <= i < biggest; a[biggest] > a[i]; // the first biggest found is the 'biggest'
        //@ maintaining \forall int i; biggest <= i < index; a[biggest] >= a[i]; // even for duplicates, the first found is kept
        //@ loop_writes biggest, index;
        //@ decreases a.length - index;
        while (a.length - index > 0) {
            if (a[index] > a[biggest]) {
                biggest = index;
            }
            index = index + 1;
        }
        return biggest;
    }
}
