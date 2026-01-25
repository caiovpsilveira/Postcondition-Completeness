import os
from pathlib import Path
import subprocess
import threading
import argparse
import queue
import sys
import shutil

NUM_RUNS = 10

NUM_THREADS = 8


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


def _append_subprocess_stderr(path: Path, result: subprocess.CompletedProcess[str]) -> None:
    if not result.stderr:
        return
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n{result.stderr}\n")


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
    run_idx: int,
    thread_idx: int,
    filepath: Path,
    thread_tmp_dir: Path,
    annotated_index: dict[str, Path],
):
    print(f"Running {filepath}")
    classname = filepath.stem

    output_dir = Path(f"results_{exp_name}") / f"run_{run_idx}"
    # Note: directories are pre-created at startup, no mkdir needed here

    exp_settings_str = get_experiment_settings(exp_name)
    completeness_check_flags = get_completeness_check_flags(exp_name)

    # Temp layout:
    # - thread_tmp_dir is unique per (exp, pid, thread)
    # - inside it, specgen gets its own subdir
    specgen_tmp_dir = thread_tmp_dir / "specgen"
    specgen_tmp_dir.mkdir(parents=True, exist_ok=True)

    # Unique per-job temporary filename for completeness/equivalence tests.
    temporary_filename = thread_tmp_dir / f"{classname}_r{run_idx}_tmp.java"

    # Put specgen log directly into the run directory to avoid global ./logs collisions.
    log_filename = f"log_{classname}.txt"
    log_path = output_dir / log_filename

    # 10 runs, each with 10 attempts for the LLM
    specgen_cmd = [
        sys.executable,
        "specgen/specgen.py",
        "--input",
        str(filepath),
        "--log_file",
        str(log_path),
        "--tmp_dir",
        str(specgen_tmp_dir),
        *_split_flags(exp_settings_str),
    ]
    specgen_result = subprocess.run(specgen_cmd, capture_output=True, text=True)

    print(f'{specgen_result.stdout}\n{specgen_result.stderr}')

    wrote_fallback_log = False
    if not log_path.exists():
        # If specgen failed before creating the log, still persist stdout/stderr for debugging.
        _ensure_file(log_path)
        _append_subprocess_output(log_path, specgen_result)
        wrote_fallback_log = True

    if specgen_result.returncode == 0:
        # Generated a valid result.
        # If embedded completeness is enabled, 0 means that it's also complete
        # NOTE: if the embedded completeness is enabled, a rc != 0 might mean that it's a true failure, or that it generated a valid, but not complete.
        # We need to check in the logs to see if it was a 'too weak' message. In this case, it was valid (but not complete).
        # get_statistics_from_logs.py handles that. (extract_stats function)
        equiv_cmd = [
            sys.executable,
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
                        sys.executable,
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

    # log is already in output_dir; specgen mirrors log content to stdout,
    # so only append stderr to avoid duplicating the whole log.
    # If we had to create a fallback log (specgen crashed early), stderr is already included.
    if not wrote_fallback_log:
        _append_subprocess_stderr(log_path, specgen_result)

def worker(
    exp_name: str,
    thread_idx: int,
    jobs: "queue.Queue[tuple[int, Path]]",
    annotated_index: dict[str, Path],
):
    # Unique per-process+experiment+thread temp dir to avoid collisions even
    # if multiple experiment runners are launched concurrently.
    thread_tmp_root = Path("tmp") / f"runexp_{exp_name}_p{os.getpid()}_t{thread_idx}"
    thread_tmp_root.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            run_idx, filepath = jobs.get_nowait()
        except queue.Empty:
            return

        filepath = Path(filepath)
        classname = filepath.stem
        # Per-job temp dir (prevents any chance of OpenJML considering multiple
        # unrelated .java files sitting side-by-side).
        job_tmp_dir = thread_tmp_root / f"{classname}_r{run_idx}"
        job_tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            process_file(exp_name, run_idx, thread_idx, filepath, job_tmp_dir, annotated_index)
        except Exception as e:
            print(f"[Thread {thread_idx}] Error processing {filepath} (run {run_idx}): {e}")
        finally:
            jobs.task_done()

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


def _cleanup_tmp_dirs(exp_name: str, pid: int) -> None:
    tmp_root = Path("tmp")
    if not tmp_root.exists():
        return

    # Only delete the directories created by this runner (same exp + pid).
    # Pattern matches the thread-specific roots created in worker().
    pattern = f"runexp_{exp_name}_p{pid}_t*"
    for p in tmp_root.glob(pattern):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)

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

    total_jobs = NUM_RUNS * len(dataset)
    print(f"Scheduling {total_jobs} jobs ({NUM_RUNS} runs x {len(dataset)} files)")

    # Pre-create run directories
    for run_idx in range(NUM_RUNS):
        run_dir = Path(f"results_{exp_name}") / f"run_{run_idx}"
        run_dir.mkdir(parents=True, exist_ok=True)

    jobs: "queue.Queue[tuple[int, Path]]" = queue.Queue()
    for run_idx in range(NUM_RUNS):
        for filepath in dataset:
            jobs.put((run_idx, Path(filepath)))

    num_threads = min(NUM_THREADS, total_jobs)
    threads: list[threading.Thread] = []
    for thread_idx in range(num_threads):
        t = threading.Thread(
            target=worker,
            args=(exp_name, thread_idx, jobs, annotated_index),
            name=f"worker-{thread_idx}",
            daemon=False,
        )
        t.start()
        threads.append(t)

    # Wait for all jobs to finish
    jobs.join()
    for t in threads:
        t.join()

    _cleanup_tmp_dirs(exp_name, os.getpid())

    print(f"Finished experiment")
