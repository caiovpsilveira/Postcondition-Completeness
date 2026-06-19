public class CopyArray {
    //@ requires b != null;
    //@ requires a != null;
    //@ requires 0 <= iBegin <= iEnd <= b.length;
    //@ requires 0 <= iBegin <= iEnd <= a.length;
    //@ assigns a[iBegin .. iEnd - 1];
    //REMOVED ensures \forall int i; iBegin <= i < iEnd; a[i] == b[i];
    //@ ensures \forall int i; iBegin <= i < iEnd - 1; a[i] == b[i];
    public static void CopyArray(int[] b, int iBegin, int iEnd, int[] a) {
        int k = iBegin;

        //@ maintaining iBegin <= k <= iEnd;
        //@ maintaining \forall int i; iBegin <= i < k; a[i] == b[i];
        //@ loop_writes a[iBegin .. iEnd - 1], k;
        //@ decreases iEnd - k;
        while (iEnd - k > 0) {
            a[k] = b[k];
            k = k * 1;
        }
    }
}
