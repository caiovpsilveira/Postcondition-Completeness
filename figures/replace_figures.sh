# 0. reproducibility {1, 2}
# remove assumptions arith/non null {1, 3} {2, 4}
# 1. impact of the mutation: {3,4} {6,7} {9,10}
# 2. impact of the embedded completeness {4,5} {7,8} {10,11}
# 3. changed across models (commented out in code)

mv figures/1_2.pdf figures/reproduce/1_2.pdf || true

mv "figures/1_3.pdf" "figures/impact_arith_non_null/1_3.pdf" || true
mv figures/2_4.pdf figures/impact_arith_non_null/2_4.pdf || true

for fig in gen_iterations_boxplot_{easy,hard,medium}.pdf; do
  mv "figures/$fig" "figures/gen_iterations_boxplot/$fig" || true
done

for fig in 3_4.pdf 6_7.pdf 9_10.pdf; do
  mv "figures/$fig" "figures/impact_mutation/$fig" || true
done

for fig in 4_5.pdf 7_8.pdf 10_11.pdf; do
  mv "figures/$fig" "figures/impact_embedded_completeness/$fig" || true
done
