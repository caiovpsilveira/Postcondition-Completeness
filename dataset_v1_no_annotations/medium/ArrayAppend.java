public class ArrayAppend {
    public static int[] arrayAppend(int[] a, int elem) {
        int[] copy = new int[a.length + 1];
        for (int i = 0; i < a.length; ++i) {
            copy[i] = a[i];
        }
        copy[copy.length - 1] = elem;
        return copy;
    }
}
