public class Find {
    public static int find(int[] arr, int elem) {
        if (arr == null)
            return -1;

        for (int i = 0; i < arr.length; i++)
            if (arr[i] == elem)
                return i;
        return -1;
    }
}
