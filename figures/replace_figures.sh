# 0. reproducibility {1, 2}
# remove assumptions arith/non null {1, 3} {2, 4}
# 1. impact of the mutation: {3,4} {8,9} {13,14}
# 2. impact of the prompt {4,5} {6,7} {9,10} {11,12}{14,15}{16,17}
# 3. impact of the embedded completeness {4,6} {5,7} {9,11} {10,12} {14, 16} {15,17}
# 4. changed accross models {3,8,13} {4,9,14} {5,10,15} {6,11,16} {7,12,17}

mv figures/1_2.pdf figures/reproduce/1_2.pdf

mv "figures/1_3.pdf" "figures/impact_arith_non_null/1_3.pdf"
mv figures/2_4.pdf figures/impact_arith_non_null/2_4.pdf

for fig in gen_iterations_boxplot_{easy,hard,medium}.pdf; do
  mv "figures/$fig" "figures/gen_iterations_boxplot/$fig"
done

for fig in 3_8_13.pdf 4_9_14.pdf 5_10_15.pdf 6_11_16.pdf 7_12_17.pdf; do
  mv "figures/$fig" "figures/changes_across_models/$fig"
done

for fig in 4_6.pdf 5_7.pdf 9_11.pdf 10_12.pdf 14_16.pdf 15_17.pdf; do
  mv "figures/$fig" "figures/impact_embedded_completeness/$fig"
done

for fig in 3_4.pdf 8_9.pdf 13_14.pdf; do
  mv "figures/$fig" "figures/impact_mutation/$fig"
done

for fig in 4_5.pdf 6_7.pdf 9_10.pdf 11_12.pdf 14_15.pdf 16_17.pdf; do
  mv "figures/$fig" "figures/prompt_influence/$fig"
done
