public class AllUnique2 {
    public static boolean allUnique(int[] sortedArray) {
        for (int i = 1; i < sortedArray.length; i++) {
            if (sortedArray[i] == sortedArray[i - 1]) {
                return false;
            }
        }
        return true;
    }
}
