set -euo pipefail

input_dir="dataset_v1_annotated"
out_dir="compl_outputs"
mkdir -p "$out_dir"

shopt -s nullglob
for path in "$input_dir"/*; do
    file="$(basename "$path")"
    out_file="$out_dir/${file%.*}.java"

    if openjml --esc --nullable-by-default --timeout 300 "$path" &> /dev/null; then
        : # echo "OpenJML passed for $file" >&2
    else
        echo "FAILED: OpenJML FAILED for $file" >&2
    fi

    if python src/equivalence_check.py "$path" -no_check_feas --to_file "$out_file" &> /dev/null; then
        : # echo "Completeness check passed for $file" >&2
    else
        echo "FAILED: Completeness check FAILED for $file" >&2
    fi
done