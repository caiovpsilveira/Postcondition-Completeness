import os
from pathlib import Path
import subprocess
import threading
import argparse

NUM_RUNS = 1

NUM_THREADS = 8

# note: this is only to parallelize one RUN, parallelizing each attempt
# because today the log is stored in like logs/log_Mul.java
# we would need to change this to support parallelizing {num_runs * num_files}
def split_dataset_n_chunks(dataset, num_chunks):
    """Split dataset into num_chunks roughly equal parts."""
    chunk_size = len(dataset) // num_chunks
    remainder = len(dataset) % num_chunks
    
    chunks = []
    start = 0
    
    for i in range(num_chunks):
        # Distribute remainder across first chunks
        end = start + chunk_size + (1 if i < remainder else 0)
        chunks.append(dataset[start:end])
        start = end
    
    return chunks


def _split_flags(flags: str) -> list[str]:
    return flags.split() if flags else []


def _safe_replace(src: Path, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        return False
    src.replace(dst)
    return True


def _ensure_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()


def _append_subprocess_output(path: Path, result: subprocess.CompletedProcess[str]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n{result.stdout}\n\n{result.stderr}\n")


def _ground_truth_path_for_input(input_file: Path) -> Path:
    no_annot_root = Path("dataset_v1_no_annotations").resolve()
    annot_root = Path("dataset_v1_annotated").resolve()

    try:
        rel = input_file.resolve().relative_to(no_annot_root)
        return annot_root / rel
    except ValueError:
        # Fallback to old flat layout (or if input_file is outside dataset root).
        return annot_root / input_file.name


def _build_annotated_index(annotated_root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for p in annotated_root.glob("**/*.java"):
        stem = p.stem
        if stem in index and index[stem] != p:
            # Keep the first occurrence, but warn; duplicates would be ambiguous.
            print(f"[run_experiments] WARNING: duplicate annotated classname {stem}: {index[stem]} and {p}")
            continue
        index[stem] = p
    return index

def process_file(
    exp_name,
    filepath: Path,
    output_dir: Path,
    temporary_filename: Path,
    annotated_index: dict[str, Path],
):
    print(f"Running {filepath}")
    classname = filepath.stem

    exp_settings_str = get_experiment_settings(exp_name)
    completeness_check_flags = get_completeness_check_flags(exp_name)

    # 10 runs, each with 10 attempts for the LLM
    specgen_cmd = [
        "python",
        "specgen/specgen.py",
        "--input",
        str(filepath),
        *_split_flags(exp_settings_str),
    ]
    specgen_result = subprocess.run(specgen_cmd, capture_output=True, text=True)

    print(f'{specgen_result.stdout}\n{specgen_result.stderr}')

    log_filename = f"log_{classname}.txt"
    log_path = Path("logs") / log_filename

    if specgen_result.returncode == 0:
        # Passed generation phase.
        # This experiment has the equiv NOT embedded. Lets see if just asking the LLM to generate a complete code is enough.
        # NOTE: must be the LOG path (which contains the LLM generated code at the end...), the equiv test parses the log for the last
        equiv_cmd = [
            "python3",
            "src/completeness_check.py",
            str(log_path),
            "--to_file",
            str(temporary_filename),
            *_split_flags(completeness_check_flags),
        ]
        equiv_result = subprocess.run(equiv_cmd, capture_output=True, text=True)

        # Copy completeness test and append completeness log
        compl_log_path = output_dir / f"log_{classname}_compl.txt"
        if not _safe_replace(temporary_filename, compl_log_path):
            _ensure_file(compl_log_path)
            with compl_log_path.open("a", encoding="utf-8") as f:
                f.write(
                    "\n\n[run_experiments] WARNING: completeness tmp file was not created. "
                    "See subprocess output below.\n"
                )
        _append_subprocess_output(compl_log_path, equiv_result)

        if equiv_result.returncode == 0: # Passed completeness test
            # check ground truth
            if equiv_result.returncode == 0:
                ground_truth_filepath = _ground_truth_path_for_input(filepath)
                ground_truth_filepath = annotated_index.get(classname, ground_truth_filepath)
                if not ground_truth_filepath.exists():
                    print(
                        f"[run_experiments] Missing ground truth for {classname}: {ground_truth_filepath}"
                    )
                else:
                    logical_equiv_cmd = [
                        "python3",
                        "src/logical_equivalence_check.py",
                        str(log_path),
                        str(ground_truth_filepath),
                        "--to_file",
                        str(temporary_filename),
                        *_split_flags(completeness_check_flags),
                    ]
                    logical_equiv_GT_result = subprocess.run(
                        logical_equiv_cmd, capture_output=True, text=True
                    )

                    logical_equiv_log_path = output_dir / f"log_{classname}_logical_equiv_GT.txt"
                    if not _safe_replace(temporary_filename, logical_equiv_log_path):
                        _ensure_file(logical_equiv_log_path)
                        with logical_equiv_log_path.open("a", encoding="utf-8") as f:
                            f.write(
                                "\n\n[run_experiments] WARNING: logical-equivalence tmp file was not created. "
                                "See subprocess output below.\n"
                            )
                    _append_subprocess_output(logical_equiv_log_path, logical_equiv_GT_result)

    # Copy log
    run_log_path = output_dir / log_filename
    if not _safe_replace(log_path, run_log_path):
        _ensure_file(run_log_path)
        with run_log_path.open("a", encoding="utf-8") as f:
            f.write(
                "\n\n[run_experiments] WARNING: expected specgen log file was not found at "
                f"{log_path}.\n"
            )
        _append_subprocess_output(run_log_path, specgen_result)

def worker(exp_name, thread_idx, files_chunk, output_dir: Path, annotated_index: dict[str, Path]):
    for filepath in files_chunk:
        filepath = Path(filepath)
        classname = filepath.stem
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_name = tmp_dir / f"{classname}_{thread_idx}_tmp.java"
        try:
            process_file(exp_name, filepath, output_dir, tmp_name, annotated_index)
        except Exception as e:
            print(f"[Thread {thread_idx}] Error processing {filepath}: {e}")

def get_experiment_settings(exp):
    if exp == "E1":
        return "--model gpt-3.5-turbo --prompt_type original --mutation --use_nonnull_and_no_ovf_asm"
    elif exp == "E2":
        return "--model gpt-3.5-turbo --prompt_type original --use_nonnull_and_no_ovf_asm"

    elif exp == "E3":
        return "--model gpt-3.5-turbo --prompt_type original --mutation"
    elif exp == "E4":
        return "--model gpt-3.5-turbo --prompt_type original"
    elif exp == "E5":
        return "--model gpt-3.5-turbo --prompt_type strict"
    elif exp == "E6":
        return "--model gpt-3.5-turbo --prompt_type original --embedded_compl"
    elif exp == "E7":
        return "--model gpt-3.5-turbo --prompt_type strict --embedded_compl"

    elif exp == "E8":
        return "--model gpt-4.1-mini --prompt_type original --mutation"
    elif exp == "E9":
        return "--model gpt-4.1-mini --prompt_type original"
    elif exp == "E10":
        return "--model gpt-4.1-mini --prompt_type strict"
    elif exp == "E11":
        return "--model gpt-4.1-mini --prompt_type original --embedded_compl"
    elif exp == "E12":
        return "--model gpt-4.1-mini --prompt_type strict --embedded_compl"

    elif exp == "E13":
        return "--model gpt-5-mini --prompt_type original --mutation"
    elif exp == "E14":
        return "--model gpt-5-mini --prompt_type original"
    elif exp == "E15":
        return "--model gpt-5-mini --prompt_type strict"
    elif exp == "E16":
        return "--model gpt-5-mini --prompt_type original --embedded_compl"
    elif exp == "E17":
        return "--model gpt-5-mini --prompt_type strict --embedded_compl"
    else:
        assert 0
        return ""

def get_completeness_check_flags(exp):
    if exp == "E1" or exp == "E2":
        return "-no_check_null -no_check_arith"
    else:
        return ""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp",
                        choices=["E1", "E2", "E3", "E4", "E5", "E6", "E7",
                                 "E8", "E9", "E10", "E11", "E12",
                                 "E13", "E14", "E15", "E16", "E17"], required=True)
    args = parser.parse_args()
    exp_name = args.exp

    dataset_no_annotations_path = Path('dataset_v1_no_annotations')
    dataset = list(dataset_no_annotations_path.glob('**/*.java'))

    annotated_root = Path("dataset_v1_annotated")
    annotated_index = _build_annotated_index(annotated_root)

    num_threads = min(NUM_THREADS, len(dataset))

    chunks = split_dataset_n_chunks(dataset, num_threads)

    for i in range(0, NUM_RUNS):

        print(f'run {i}')
        run_dir = Path(f"results_{exp_name}") / f"run_{i}"
        run_dir.mkdir(parents=True, exist_ok=True)

        # Create N threads
        # Each thread will have a chunk
        # Each thread will process all files in the chunk
        # After processing all files from the run, wait until all threads finish
        # Then proceed to next run (outer loop)
        threads = []
        for idx, chunk in enumerate(chunks):
            t = threading.Thread(
                target=worker,
                args=(exp_name, idx, chunk, run_dir, annotated_index),
                name=f"worker-{i}-{idx}",
            )
            t.start()
            threads.append(t)

        # After processing all files from the run, wait until all threads finish
        for t in threads:
            t.join()

    print(f"Finished experiment")
