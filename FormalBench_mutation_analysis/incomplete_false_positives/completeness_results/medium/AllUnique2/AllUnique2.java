public class AllUnique2 {
    //@ requires sortedArray != null;
    //@ requires \forall int i; 0 <= i && i < sortedArray.length - 1; sortedArray[i] <= sortedArray[i + 1];
    //@ assigns \nothing;
    //REMOVED ensures \result == \forall int i; 1 <= i && i < sortedArray.length; sortedArray[i] != sortedArray[i - 1];
    //@ ensures (\forall int i; 1 <= i && i < sortedArray.length; sortedArray[i] != sortedArray[i - 1]) ==> \result == true;
    public static boolean allUnique(int[] sortedArray) {
        //@ maintaining 1 <= i <= sortedArray.length || i == 1;
        //@ maintaining \forall int j; 1 <= j < i; sortedArray[j] != sortedArray[j - 1];
        //@ loop_writes i;
        //@ decreases sortedArray.length - i;
        for (int i = 1; i < sortedArray.length; i++) {
            if (sortedArray[i] == sortedArray[i - 1]) {
                return false;
            }
        }
        return true;
    }
}
