public class AllUnique {
    public static boolean allUnique(int[] arr) {
        if (arr == null) return true;

        for (int i = 0; i < arr.length - 1; i++) {
            for (int j = i + 1; j < arr.length; j++) {
                if (arr[i] == arr[j]) {
                    return false;
                }
            }
        }
        return true;
    }
}
