public class IsReverseArray {
    public static boolean isReverseArray(int[] x, int[] y) {
        if (x.length != y.length)
            return false;
        int index = 0;

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
