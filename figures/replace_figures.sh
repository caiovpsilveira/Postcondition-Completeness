# 1. impact of the mutation: {1,2} {4,5} {7,8}
# 2. impact of the embedded completeness {2,3} {5,6} {8,9}
# 3. changed across models (commented out in code)

for fig in gen_iterations_boxplot_{easy,hard,medium}.pdf; do
  mv "figures/$fig" "figures/gen_iterations_boxplot/$fig" || true
done

for fig in 1_2.pdf 4_5.pdf 7_8.pdf; do
  mv "figures/$fig" "figures/impact_mutation/$fig" || true
done

for fig in 2_3.pdf 5_6.pdf 8_9.pdf; do
  mv "figures/$fig" "figures/impact_embedded_completeness/$fig" || true
done
