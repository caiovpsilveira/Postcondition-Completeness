package src.completeness.util;

public final class CompletenessUtil
{

// NOTE: avoid using generics (?).
// In the dataset we want to make sure
// That the proper equality/deep clone is being used
// Also if not present, better to caught it earlier

// Also, float and double are using '==' checks. this will check exact binary equality.
// this is bad for floats and double, and you should usually account for epsilon

// Plain types (and String)

public static boolean Equals(boolean a, boolean b) {
    return a == b;
}

public static boolean Equals(char a, char b) {
    return a == b;
}

public static boolean Equals(short a, short b) {
    return a == b;
}

public static boolean Equals(int a, int b) {
    return a == b;
}

public static boolean Equals(long a, long b) {
    return a == b;
}

public static boolean Equals(float a, float b) {
    return a == b;
}

public static boolean Equals(double a, double b) {
    return a == b;
}

public static boolean Equals(String a, String b) {
    if (a == b) return true;
    if (a == null || b == null) return false;
    return a.equals(b);
}

// Arrays
public static boolean Equals(boolean[] a, boolean[] b) {
    if (a == b) return true;
    if (a == null || b == null) return false;
    if (a.length != b.length) return false;
    //@ maintaining 0 <= i <= a.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(a[j], b[j]);
    //FIXME below is redundant but otherwise OpenJML struggles
    //@ maintaining \forall int j; 0 <= j < i; a[j] == b[j];
    //@ loop_writes i;
    //@ decreases a.length - i;
    for (int i = 0; i < a.length; i++) {
        if (!Equals(a[i], b[i])) return false;
    }
    return true;
}

public static boolean Equals(char[] a, char[] b) {
    if (a == b) return true;
    if (a == null || b == null) return false;
    if (a.length != b.length) return false;
    //@ maintaining 0 <= i <= a.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(a[j], b[j]);
    //FIXME below is redundant but otherwise OpenJML struggles
    //@ maintaining \forall int j; 0 <= j < i; a[j] == b[j];
    //@ loop_writes i;
    //@ decreases a.length - i;
    for (int i = 0; i < a.length; i++) {
        if (!Equals(a[i], b[i])) return false;
    }
    return true;
}

public static boolean Equals(short[] a, short[] b) {
    if (a == b) return true;
    if (a == null || b == null) return false;
    if (a.length != b.length) return false;
    //@ maintaining 0 <= i <= a.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(a[j], b[j]);
    //FIXME below is redundant but otherwise OpenJML struggles
    //@ maintaining \forall int j; 0 <= j < i; a[j] == b[j];
    //@ loop_writes i;
    //@ decreases a.length - i;
    for (int i = 0; i < a.length; i++) {
        if (!Equals(a[i], b[i])) return false;
    }
    return true;
}

public static boolean Equals(int[] a, int[] b) {
    if (a == b) return true;
    if (a == null || b == null) return false;
    if (a.length != b.length) return false;
    //@ maintaining 0 <= i <= a.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(a[j], b[j]);
    //FIXME below is redundant but otherwise OpenJML struggles
    //@ maintaining \forall int j; 0 <= j < i; a[j] == b[j];
    //@ loop_writes i;
    //@ decreases a.length - i;
    for (int i = 0; i < a.length; i++) {
        if (!Equals(a[i], b[i])) return false;
    }
    return true;
}

public static boolean Equals(long[] a, long[] b) {
    if (a == b) return true;
    if (a == null || b == null) return false;
    if (a.length != b.length) return false;
    //@ maintaining 0 <= i <= a.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(a[j], b[j]);
    //FIXME below is redundant but otherwise OpenJML struggles
    //@ maintaining \forall int j; 0 <= j < i; a[j] == b[j];
    //@ loop_writes i;
    //@ decreases a.length - i;
    for (int i = 0; i < a.length; i++) {
        if (!Equals(a[i], b[i])) return false;
    }
    return true;
}

public static boolean Equals(float[] a, float[] b) {
    if (a == b) return true;
    if (a == null || b == null) return false;
    if (a.length != b.length) return false;
    //@ maintaining 0 <= i <= a.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(a[j], b[j]);
    //FIXME below is redundant but otherwise OpenJML struggles
    //@ maintaining \forall int j; 0 <= j < i; a[j] == b[j];
    //@ loop_writes i;
    //@ decreases a.length - i;
    for (int i = 0; i < a.length; i++) {
        if (!Equals(a[i], b[i])) return false;
    }
    return true;
}

public static boolean Equals(double[] a, double[] b) {
    if (a == b) return true;
    if (a == null || b == null) return false;
    if (a.length != b.length) return false;
    //@ maintaining 0 <= i <= a.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(a[j], b[j]);
    //FIXME below is redundant but otherwise OpenJML struggles
    //@ maintaining \forall int j; 0 <= j < i; a[j] == b[j];
    //@ loop_writes i;
    //@ decreases a.length - i;
    for (int i = 0; i < a.length; i++) {
        if (!Equals(a[i], b[i])) return false;
    }
    return true;
}

// TODO: this is getting some weird error at OpenJML
// public static boolean Equals(String[] a, String[] b) {
//     if (a == b) return true;
//     if (a == null || b == null) return false;
//     if (a.length != b.length) return false;
//     //@ maintaining 0 <= i <= a.length;
//     //@ maintaining \forall int j; 0 <= j < i; Equals(a[j], b[j]);
//     //FIXME below is redundant but otherwise OpenJML struggles
//     //@ maintaining \forall int j; 0 <= j < i; a[j] == b[j];
//     //@ loop_writes i;
//     //@ decreases a.length - i;
//     for (int i = 0; i < a.length; i++) {
//         if (!Equals(a[i], b[i])) return false;
//     }
//     return true;
// }

// Matrices

public static boolean Equals(int[][] a, int[][] b) {
    if (a == b) return true;
    if (a == null || b == null) return false;
    if (a.length != b.length) return false;
    //@ maintaining 0 <= i <= a.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(a[j], b[j]);
    // FIXME below is redundant but otherwise OpenJML struggles
    //@ maintaining \forall int j; 0 <= j && j < i;
    //@   (a[j] == b[j]) ||
    //@   (a[j] != null && b[j] != null
    //@     && a[j].length == b[j].length
    //@     && (\forall int k; 0 <= k && k < a[j].length;
    //@           a[j][k] == b[j][k]));
    //@ loop_writes i;
    //@ decreases a.length - i;
    for (int i = 0; i < a.length; i++) {
        if (!Equals(a[i], b[i])) return false;
    }
    return true;
}



// Deep clones: plain types (and String)

public static boolean DeepCopy(boolean a) {
    return a;
}

public static char DeepCopy(char a) {
    return a;
}

public static short DeepCopy(short a) {
    return a;
}

public static int DeepCopy(int a) {
    return a;
}

public static long DeepCopy(long a) {
    return a;
}

public static float DeepCopy(float a) {
    return a;
}

public static double DeepCopy(double a) {
    return a;
}

public static String DeepCopy(String a) {
    if (a == null) return null;
    return new String(a);
}

// Deep clones: Arrays

public static boolean[] DeepCopy(boolean[] a) {
    if (a == null) return null;
    boolean[] ret = new boolean[a.length];
    //@ maintaining 0 <= i <= ret.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(ret[j], a[j]);
    //@ loop_writes i, ret[*];
    //@ decreases ret.length - i;
    for (int i = 0; i < ret.length; i++) {
        ret[i] = DeepCopy(a[i]);
    }
    return ret;
}

public static char[] DeepCopy(char[] a) {
    if (a == null) return null;
    char[] ret = new char[a.length];
    //@ maintaining 0 <= i <= ret.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(ret[j], a[j]);
    //@ loop_writes i, ret[*];
    //@ decreases ret.length - i;
    for (int i = 0; i < ret.length; i++) {
        ret[i] = DeepCopy(a[i]);
    }
    return ret;
}

public static short[] DeepCopy(short[] a) {
    if (a == null) return null;
    short[] ret = new short[a.length];
    //@ maintaining 0 <= i <= ret.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(ret[j], a[j]);
    //@ loop_writes i, ret[*];
    //@ decreases ret.length - i;
    for (int i = 0; i < ret.length; i++) {
        ret[i] = DeepCopy(a[i]);
    }
    return ret;
}

public static int[] DeepCopy(int[] a) {
    if (a == null) return null;
    int[] ret = new int[a.length];
    //@ maintaining 0 <= i <= ret.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(ret[j], a[j]);
    //@ loop_writes i, ret[*];
    //@ decreases ret.length - i;
    for (int i = 0; i < ret.length; i++) {
        ret[i] = DeepCopy(a[i]);
    }
    return ret;
}

public static long[] DeepCopy(long[] a) {
    if (a == null) return null;
    long[] ret = new long[a.length];
    //@ maintaining 0 <= i <= ret.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(ret[j], a[j]);
    //@ loop_writes i, ret[*];
    //@ decreases ret.length - i;
    for (int i = 0; i < ret.length; i++) {
        ret[i] = DeepCopy(a[i]);
    }
    return ret;
}

public static float[] DeepCopy(float[] a) {
    if (a == null) return null;
    float[] ret = new float[a.length];
    //@ maintaining 0 <= i <= ret.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(ret[j], a[j]);
    //@ loop_writes i, ret[*];
    //@ decreases ret.length - i;
    for (int i = 0; i < ret.length; i++) {
        ret[i] = DeepCopy(a[i]);
    }
    return ret;
}

public static double[] DeepCopy(double[] a) {
    if (a == null) return null;
    double[] ret = new double[a.length];
    //@ maintaining 0 <= i <= ret.length;
    //@ maintaining \forall int j; 0 <= j < i; Equals(ret[j], a[j]);
    //@ loop_writes i, ret[*];
    //@ decreases ret.length - i;
    for (int i = 0; i < ret.length; i++) {
        ret[i] = DeepCopy(a[i]);
    }
    return ret;
}

// public static String[] DeepCopy(String[] a) {
//     if (a == null) return null;
//     String[] ret = new String[a.length];
//     //@ maintaining 0 <= i <= ret.length;
//     //@ maintaining \forall int j; 0 <= j < i; Equals(ret[j], a[j]);
//     //@ loop_writes i, ret[*];
//     //@ decreases ret.length - i;
//     for (int i = 0; i < ret.length; i++) {
//         ret[i] = DeepCopy(a[i]);
//     }
//     return ret;
// }

}
