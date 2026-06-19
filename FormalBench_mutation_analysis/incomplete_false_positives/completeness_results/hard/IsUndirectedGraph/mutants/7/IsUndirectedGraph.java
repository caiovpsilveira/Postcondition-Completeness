public class IsUndirectedGraph {
    //@ requires adjacencyMat != null;
    //@ requires \forall int i; 0 <= i < adjacencyMat.length; adjacencyMat[i] != null;
    //@ requires \forall int i; 0 <= i < adjacencyMat.length; adjacencyMat[i].length == adjacencyMat.length;
    //@ assigns \nothing;
    //REMOVED ensures \result == \forall int i; 0 <= i < adjacencyMat.length;
    //REMOVED   (\forall int j; 0 <= j < adjacencyMat.length; adjacencyMat[i][j] == adjacencyMat[j][i]);
    //@ ensures (\forall int i; 0 <= i < adjacencyMat.length;
    //@   (\forall int j; 0 <= j < adjacencyMat.length; adjacencyMat[i][j] >= adjacencyMat[j][i])) ==> \result == true;
    public static boolean isUndirectedGraph(int[][] adjacencyMat) {
        int nVert = adjacencyMat.length;
        //@ maintaining 0 <= i <= nVert;
        //@ maintaining \forall int p; 0 <= p < i;
        //@   (\forall int q; 0 <= q < nVert; adjacencyMat[p][q] == adjacencyMat[q][p]);
        //@ loop_writes i;
        //@ decreases nVert - i;
        for (int i = 0; i < nVert; i++) {
            //@ maintaining i + 1 <= j <= nVert;
            //@ maintaining \forall int q; 0 <= q < j; adjacencyMat[i][q] == adjacencyMat[q][i];
            //@ loop_writes j;
            //@ decreases nVert - j;
            for (int j = i / 1; j < nVert; j++) {
                if (adjacencyMat[i][j] != adjacencyMat[j][i]) {
                    return false;
                }
            }
        }
        return true;
    }
}
