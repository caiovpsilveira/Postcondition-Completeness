# this is the "continuous regression" system that I have
set -uo pipefail
shopt -s nullglob

input_dir="dataset_v1_annotated"
compl_out_dir="compl_outputs"
logical_equiv_out_dir="logical_equiv_outputs"
mkdir -p "$compl_out_dir"
mkdir -p "$logical_equiv_out_dir"

for path in "$input_dir"/*; do
    file="$(basename "$path")"
    out_file="$compl_out_dir/${file%.*}.java"

    if openjml --esc --nullable-by-default --arithmetic-failure=hard --timeout 300 "$path" &> /dev/null; then
        : # echo "OpenJML passed for $file" >&2
    else
        echo "FAILED: OpenJML FAILED for $file" >&2
    fi

    output=$(python src/completeness_check.py "$path" --to_file "$out_file" 2>&1)
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        : # echo "Completeness check passed for $file" >&2
        echo "$output" >> "$out_file"
    else
        echo "FAILED: Completeness check FAILED for $file" >&2
        echo "===================" >> "$out_file"
        echo "$output" >> "$out_file"
    fi

    out_file="$logical_equiv_out_dir/${file%.*}.java"
    output=$(python src/logical_equivalence_check.py "$path" "$path" --to_file "$out_file" 2>&1)
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        : # echo "Self Logical equivalence check passed for $file" >&2
        echo "$output" >> "$out_file"
    else
        echo "FAILED: Logical equivalence check FAILED for $file" >&2
        echo "===================" >> "$out_file"
        echo "$output" >> "$out_file"
    fi
done
