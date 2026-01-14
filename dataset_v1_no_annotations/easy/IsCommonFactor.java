public class IsCommonFactor {
    public static boolean isCommonFactor(int a, int b, int factor) {
        if (a % factor == 0 && b % factor == 0)
            return true;
        return false;
    }
}
