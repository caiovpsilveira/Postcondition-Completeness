public class IsUndirectedGraph {
    public static boolean isUndirectedGraph(int[][] adjacencyMat) {
        int nVert = adjacencyMat.length;

        for (int i = 0; i < nVert; i++) {
            for (int j = i + 1; j < nVert; j++) {
                if (adjacencyMat[i][j] != adjacencyMat[j][i]) {
                    return false;
                }
            }
        }
        return true;
    }
}
