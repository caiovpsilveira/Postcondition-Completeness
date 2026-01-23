import os
import re
from collections import deque
import pandas as pd
import argparse
from simple_tokenizer_java import simple_tokenize_java
from pathlib import Path

NUM_RUNS = 10

# parses log into spec/code
from file_processor import process_file

def list_all_files_os_walk(directory_path):
    file_paths = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_paths.append(full_path)
    return file_paths

def tail(path, n):
    if n <= 0:
        return ""
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = list(deque(f, maxlen=n))
            return ''.join(lines)
    except Exception:
        return ""


_RETURN_CODE_FOOTER_RE = re.compile(r"Return Code: (\d+)\n\n\n\n\Z")


def get_return_code_if_valid_footer(path: str, *, read_bytes: int = 4096) -> int | None:
    """Return the trailing Return Code if the file ends with the expected footer.

    Expected footer (must be at end-of-file):
        Return Code: <int>\n\n\n\n
    """
    try:
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - read_bytes), os.SEEK_SET)
            tail_bytes = f.read(read_bytes)
        tail_text = tail_bytes.decode('utf-8', errors='replace')
    except Exception:
        return None

    m = _RETURN_CODE_FOOTER_RE.search(tail_text)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None

def get_reverse_classification_map():
    dataset_no_annotations_path = Path('dataset_v1_no_annotations')
    easy_path = dataset_no_annotations_path / 'easy'
    medium_path = dataset_no_annotations_path / 'medium'
    hard_path = dataset_no_annotations_path / 'hard'

    difficulty_map = {}

    for file in easy_path.glob('**/*.java'):
        classname = file.stem
        difficulty_map[classname] = 'easy'

    for file in medium_path.glob('**/*.java'):
        classname = file.stem
        difficulty_map[classname] = 'medium'

    for file in hard_path.glob('**/*.java'):
        classname = file.stem
        difficulty_map[classname] = 'hard'

    return difficulty_map


def find_original_source_file(classname: str) -> Path | None:
    """Find the original (no-annotations) Java file for a classname.

    Supports both the old flat layout and the new easy/medium/hard subdirectories.
    """
    root = Path("dataset_v1_no_annotations")
    # New layout: dataset_v1_no_annotations/{easy,medium,hard}/Class.java
    candidates = list(root.glob(f"**/{classname}.java"))
    if candidates:
        return candidates[0]
    # Old layout fallback
    flat = root / f"{classname}.java"
    if flat.exists():
        return flat
    return None

def extract_stats(results_dirs):
    # Parse logs to create a dataframe with
    # 'run,difficulty,classname,result,time,number_of_iterations_before_first_valid,number_of_iterations'

    # Array to create dataframe
    run_records = []

    dataset_files = list_all_files_os_walk("dataset_v1_no_annotations")

    difficulty_map = get_reverse_classification_map()

    for exp_dir in results_dirs:
        log_files = set(list_all_files_os_walk(exp_dir))

        for file in dataset_files:
            classname = file.split('/')[-1].split('.')[0]

            for i in range(0, NUM_RUNS): # assumes NUM_RUNS runs exists
                #print(f'Processing {classname}, run {i}')

                # Check existence of log files.
                # If only log_{classname}.txt exists, it can be either a true failure or a 'valid' with embedded completeness,
                # that failed to prove complete. Need to check if "too weak" message exists
                # If log_{classname}_compl.txt exists, it is valid
                # If log_{classname}_logical_equiv_GT.txt exists, it suceed completeness check

                base = os.path.join(exp_dir, f'run_{i}')

                log = os.path.join(base, f'log_{classname}.txt')
                if not log in log_files:
                    print(f'Missing log file: {log}')
                    continue

                log_equiv_gt = os.path.join(base, f'log_{classname}_logical_equiv_GT.txt')
                log_compl = os.path.join(base, f'log_{classname}_compl.txt')

                compl_rc: int | None = None
                gt_rc: int | None = None

                if log_compl in log_files:
                    compl_rc = get_return_code_if_valid_footer(log_compl)
                    if compl_rc is None:
                        print(
                            "Warning: completeness log has unexpected ending; expected "
                            "'Return Code: <int>\\n\\n\\n\\n' at EOF: "
                            f"{log_compl}"
                        )

                if log_equiv_gt in log_files:
                    gt_rc = get_return_code_if_valid_footer(log_equiv_gt)
                    if gt_rc is None:
                        print(
                            "Warning: logical_equiv_GT log has unexpected ending; expected "
                            "'Return Code: <int>\\n\\n\\n\\n' at EOF: "
                            f"{log_equiv_gt}"
                        )

                # get number of iterations and time
                iterations_to_first_valid = 0
                total_gen_iterations = 0
                total_mut_iterations = 0
                time = 0.0
                at_least_valid = False
                had_embedded_compl_check = False
                llm_gave_up = False
                with open(log, 'r', encoding="utf-8") as l:
                    gen_iter_pat = re.compile(r'--------------- Iteration (\d+) ---------------')
                    mut_iter_pat = re.compile(r'--------------- Mutation Iteration (\d+) ---------------')
                    gave_up_pat = re.compile(r'LLM gave up or generated incorrectly formatted code')
                    time_pat = re.compile(r'--- Elapsed time: (\d+) seconds ---')

                    for line in l:
                        matched_gen_iter = gen_iter_pat.search(line)
                        if matched_gen_iter:
                            total_gen_iterations = int(matched_gen_iter.group(1))
                        
                        matched_mut_iter = mut_iter_pat.search(line)
                        if matched_mut_iter:
                            total_mut_iterations = int(matched_mut_iter.group(1))

                        matched_time = time_pat.search(line)
                        if matched_time:
                            time = float(matched_time.group(1))

                        gave_up_match = gave_up_pat.search(line)
                        if gave_up_match:
                            llm_gave_up = True

                        if 'The specification generated is valid, but incomplete (too weak).' in line:
                            # Passed 'valid' at least once. Might have "Failure" in the log because of embedded completeness
                            # But since it was proven at least once, it's valid
                            iterations_to_first_valid = total_gen_iterations
                            at_least_valid = True
                            had_embedded_compl_check = True

                invalid_run = False
                last_log_line = tail(log, 1)
                if 'Success' in last_log_line:
                    at_least_valid = True
                    if iterations_to_first_valid == 0: # We have not found the 'too weak' message
                        # Then it's not an embedded completeness or it succeeded in generatin a complete on the first valid
                        iterations_to_first_valid = total_gen_iterations + total_mut_iterations
                elif 'Failure' in last_log_line:
                    if at_least_valid:
                        #print(f'{log} is a "completeness" failure but was valid at some point')
                        pass
                    pass # Not necessarely a failure, because of embedded completeness check
                else: # Not "Failure" or "Success" in last line. Unexpected
                    invalid_run = True
                    print(f'{log} is an invalid run') # but other files might be present...

                # Cross-file consistency checks
                ended_success = ('Success' in last_log_line)
                if at_least_valid:
                    if log_compl not in log_files:
                        reason = 'ended with Success' if ended_success else 'had "too weak" message'
                        print(
                            "Warning: missing completeness log (rule violation) for "
                            f"{exp_dir}/run_{i} {classname}: {reason}; expected {log_compl}"
                        )

                if compl_rc == 0 and log_equiv_gt not in log_files:
                    print(
                        "Warning: missing logical_equiv_GT log (rule violation) for "
                        f"{exp_dir}/run_{i} {classname}: {log_compl} ended with Return Code: 0; "
                        f"expected {log_equiv_gt}"
                    )

                result = ""
                # Store results
                if log_equiv_gt in log_files:
                    if gt_rc == 0:
                        # Success, generated something that is even equal to GT
                        result = "complete_gt"
                    else:
                        # Generated something complete, but not equal to GT
                        result = "complete"
                elif at_least_valid:
                    # generated something valid at some point (passed the verifier), but not complete
                    # result might be different than Success in the log, because of embedded completeness check
                    result = "valid"
                else:
                    if not invalid_run:
                        # True failure. LLM was unable to generate something that passed in the verifier
                        result = "failure"
                    else:
                        result = "invalid"

                if result == "":
                    print(f'Error processing {log}')
                    assert 0
                
                # These are the tests in which it did not get a complete in the first try, but the feedback loop helped:
                #if iterations_to_first_valid != 0 and iterations_to_first_valid != total_gen_iterations:
                #    print(f'{exp_dir}: run_{i} {classname}')

                difficulty = difficulty_map[classname]
                run_records.append([exp_dir, f'run_{i}', difficulty, classname, result, time, iterations_to_first_valid, total_gen_iterations, total_mut_iterations, llm_gave_up, had_embedded_compl_check])

    df = pd.DataFrame(run_records, columns=['experiment','run','difficulty','classname','result','time','number_of_iterations_before_first_valid','number_of_gen_iterations', 'number_of_mut_iterations', 'llm_gave_up', 'had_embedded_compl_check'])
    return df

# Postprocessing methods

def get_successfull_runs(df):
    mask = df['result'].astype(str).str.strip().ne('failure')
    successes = df.loc[mask].reset_index(drop=True)

    ret = []
    for row in successes.itertuples(index=False):
        #ret.append(f"reproduce_results/{row.run}/log_{row.classname}.txt")
        ret.append([row.run, row.classname])
    return ret

# See which 'successful' runs had no postcondition
def invalid_by_empty_post(df, base_dir):
    successes = get_successfull_runs(df)

    num_suc_empty_post = 0

    to_remove = []

    for entry in successes:
        logpath = os.path.join(base_dir, f'{entry[0]}/log_{entry[1]}.txt')
        specs = process_file(logpath)
        assert(len(specs)) == 1 # dataset has only one function per source file
        spec = specs[0]
        if not 'ensures' in spec.reconstruct_spec():
            print(f'has empty post: {logpath}')
            to_remove.append(entry)
            num_suc_empty_post += 1
    
    print(f'num_suc_empty_post: {num_suc_empty_post}')
    return to_remove

# See which 'successful' runs had assumptions in them
# Note: more interested in LoopInvariants assumptions
def invalid_by_assume(df, base_dir):
    successes = get_successfull_runs(df)

    num_suc_with_assumes = 0

    to_remove = []

    for entry in successes:
        logpath = os.path.join(base_dir, f'{entry[0]}/log_{entry[1]}.txt')
        specs = process_file(logpath)
        assert(len(specs)) == 1 # dataset has only one function per source file
        spec = specs[0]
        if 'assume' in spec.body:
            print(f'suc with assume: {logpath}')
            to_remove.append(entry)
            num_suc_with_assumes += 1
            
    print(f'num_successes_with_assumes: {num_suc_with_assumes}')
    return to_remove

def llm_changed_original_code(df, base_dir):
    """
    For the last entry in each log, compare non-comments with the original code.
    It should have the exact same tokens.
    """

    # are we interested in seeing on the failures as well?
    successes = get_successfull_runs(df)

    num_changed_code = 0
    to_remove = []

    for run, classname in successes:
        logpath = os.path.join(base_dir, f'{run}/log_{classname}.txt')
        original_code = find_original_source_file(classname)
        if original_code is None:
            print(f"missing original source for {classname} (looked under dataset_v1_no_annotations/**)")
            continue
        original_code_path = str(original_code)

        # the process_file function does not get the 'public class', etc.
        # just the body is relevant here, so lets process both
        specs_original = process_file(original_code_path)
        assert len(specs_original) == 1
        original_body = specs_original[0].body

        specs_result = process_file(logpath)
        assert len(specs_result) == 1  # dataset has only one function per source file
        result_body = specs_result[0].body

        orig_tokens = simple_tokenize_java(original_body)
        res_tokens = simple_tokenize_java(result_body)

        if orig_tokens != res_tokens:
            print(f'changed original code: {logpath}')
            to_remove.append([run, classname])
            num_changed_code += 1

    print(f'num_successes_with_changed_code: {num_changed_code}')
    return to_remove

# See which 'successful' runs specified exceptional behavior with 'signals' or 'signals_only'
def check_successes_with_signals(df, base_dir):
    successes = get_successfull_runs(df)

    num_suc_with_signals = 0

    to_return = []

    for entry in successes:
        logpath = os.path.join(base_dir, f'{entry[0]}/log_{entry[1]}.txt')
        specs = process_file(logpath)
        assert(len(specs)) == 1 # dataset has only one function per source file
        spec = specs[0]
        if 'signals' in spec.reconstruct_spec():
            print(f'suc with signals: {logpath}')
            to_return.append(entry) 
            num_suc_with_signals += 1

    print(f'num_successes_with_signals: {num_suc_with_signals}')
    return to_return

def mark_as_failure(df: pd.DataFrame, run, classname) -> None:
    mask = (df['run'] == run) & (df['classname'] == classname)
    df.loc[mask, 'result'] = 'failure'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process a directory with log files from 10 runs.")
    parser.add_argument("runs_dir", help="Path with the runs directory: run_0, run_1, ...")
    args = parser.parse_args()

    #results_dirs = ['results/exp1', 'results/exp2', 'results/exp3', 'results/exp4', 'results/exp5', 'results/exp6', 'results/exp7']
    all_results_dirs = [args.runs_dir]
    df = extract_stats(all_results_dirs)
    print(df)

    # postprocessing: mark as failure empty postcondition, usage of assumptions, or changes in the code
    inv1 = invalid_by_empty_post(df, args.runs_dir)
    inv2 = invalid_by_assume(df, args.runs_dir)
    inv3 = llm_changed_original_code(df, args.runs_dir)
    signals = check_successes_with_signals(df, args.runs_dir) # not invalidated, just a curiosity if any used signals

    print("\nBefore postprocessing:")
    categories = ['failure', 'valid', 'complete', 'complete_gt']
    counts = df['result'].value_counts().reindex(categories, fill_value=0)
    counts_df = counts.rename_axis('result').reset_index(name='count')
    print(counts_df.to_csv(sep=',', index=False))

    # might have intersection
    for run, classname in inv1:
        mark_as_failure(df, run, classname)

    for run, classname in inv2:
        mark_as_failure(df, run, classname)

    for run, classname in inv3:
        mark_as_failure(df, run, classname)

    print('Empty post, assume, changed code, signals') # might have intersection
    print(f'{len(inv1)},{len(inv2)},{len(inv3)},{len(signals)}\n')

    print("After postprocessing:")
    categories = ['failure', 'valid', 'complete', 'complete_gt']
    counts = df['result'].value_counts().reindex(categories, fill_value=0)
    counts_df = counts.rename_axis('result').reset_index(name='count')
    print(counts_df.to_csv(sep=',', index=False))

    # dump raw dataframe after postprocessing
    out_csv = os.path.join(args.runs_dir, 'experiments_results.csv')
    df.to_csv(out_csv, index=False)
