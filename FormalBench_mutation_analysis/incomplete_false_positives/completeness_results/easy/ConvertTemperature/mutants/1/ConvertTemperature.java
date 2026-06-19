public class ConvertTemperature {
    //@ requires celsius + 273.15 <= Double.MAX_VALUE;
    //@ requires Double.MIN_VALUE <= celsius * 1.80 + 32.00 <= Double.MAX_VALUE;
    //@ assigns \nothing;
    //@ ensures \fresh(\result);
    //REMOVED ensures \result.length == 2;
    //@ ensures \result[0] == celsius + 273.15 && \result[1] == celsius * 1.8 + 32;
    public static double[] convertTemperature(double celsius) {
        return new double[] {celsius % 273.15, celsius * 1.80 + 32.00};
    }
}
