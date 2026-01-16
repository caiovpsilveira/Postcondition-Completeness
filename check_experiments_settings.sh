#!/usr/bin/env bash

# Some of this checks rely on the probability of one of the string happening in at least 1/320 runs
# but it's sufficient for our purposes.

results_dir="$1"

if [ -z "$results_dir" ]; then
  echo "Usage: $0 <results-dir>" >&2
  exit 1
fi

# Check if directory exists
if [ ! -d "$results_dir" ]; then
  echo "Directory $results_dir does not exist." >&2
  exit 1
fi

# Check if ANY of the below are present in results_dir (literal match)
if git grep --untracked -q -F \
  -e "The prover cannot establish an assertion (PossiblyNullDeReference)" \
  -e "The prover cannot establish an assertion (ArithmeticOperationRange)" \
  -- "$results_dir"; then
  echo "null check and arith failures enabled"
else
  echo "null check and arith failures disabled"
fi

# Check if the following is present in results_dir (literal match)
if git grep --untracked -q -F \
  -e "=============== Mutation Phase ===============" \
  -- "$results_dir"; then
  echo "mutation enabled"
else
  echo "mutation disabled"
fi

# Check if ANY of the below are present in results_dir (literal match)
if git grep --untracked -q -F \
  -e "Error: You MUST NOT account for exceptional behavior" \
  -e "Error: You MUST add at least one postcondition (ensures)" \
  -e "Error: you must NOT use assumptions." \
  -- "$results_dir"; then
  echo "Forbid invalid gen"
else
  echo "Non-forbidding invalid gen"
fi

# Check if the following is present in results_dir (literal match)
# Note: verify 'withou' is intended (typo?).
if git grep --untracked -q -F \
  -e "+ You SHOULD output the code in its entirety, without omitting any original content." \
  -- "$results_dir"; then
  echo "original prompt"
else
  echo "changed prompt"
fi

# Check if the following is present in results_dir (literal match)
if git grep --untracked -q -F \
  -e "The specification generated is valid, but incomplete (too weak)" \
  -- "$results_dir"; then
  echo "embedded completeness"
else
  echo "no embedded completeness"
fi