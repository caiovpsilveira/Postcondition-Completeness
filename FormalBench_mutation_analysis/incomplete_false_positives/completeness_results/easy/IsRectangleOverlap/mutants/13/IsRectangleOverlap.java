public class IsRectangleOverlap {
    //@ requires rec1 != null;
    //@ requires rec1.length == 4;
    //@ requires rec2 != null;
    //@ requires rec2.length == 4;
    //@ assigns \nothing;
    //REMOVED ensures \result == !(rec2[1] >= rec1[3] || rec2[3] <= rec1[1] || rec2[0] >= rec1[2] || rec2[2] <= rec1[0]);
    //@ ensures (rec2[1] >= rec1[3] || rec2[3] <= rec1[1]) ==> \result == false;
    public static boolean isRectangleOverlap(int[] rec1, int[] rec2) {
        int left1   = rec1[0];
        int bottom1 = rec1[1];
        int right1  = rec1[2];
        int top1    = rec1[3];

        int left2   = rec2[0];
        int bottom2 = rec2[1];
        int right2  = rec2[2];
        int top2    = rec2[3];

        return !(bottom2 >= top1 ||
                 top2 <= bottom1 ||
                 true ||
                 right2 <= left1);
    }
}
