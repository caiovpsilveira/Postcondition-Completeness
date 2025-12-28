import os
import subprocess
import threading
import argparse

NUM_RUNS = 10

NUM_THREADS = 8

def list_all_files_os_walk(directory_path, names_only=False):
    file_paths = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_paths.append(os.path.basename(full_path) if names_only else full_path)
    return file_paths

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

def process_file(exp_name, filepath, output_dir, temporary_filename):
    print(f'Running {filepath}')
    classname = filepath.split('/')[-1].split('.')[0]

    exp_settings_str = get_experiment_settings(exp_name)
    completeness_check_flags = get_completeness_check_flags(exp_name)

    # 10 runs, each with 10 attempts for the LLM
    specgen_result = subprocess.run(f"python specgen/specgen.py --input {filepath} {exp_settings_str}",
                            shell=True, capture_output=True, text=True)

    print(f'{specgen_result.stdout}\n{specgen_result.stderr}')

    log_filename = f"log_{classname}.txt"
    log_path = f"logs/{log_filename}"

    if specgen_result.returncode == 0:
        # Passed generation phase.
        # This experiment has the equiv NOT embedded. Lets see if just asking the LLM to generate a complete code is enough.
        # NOTE: must be the LOG path (which contains the LLM generated code at the end...), the equiv test parses the log for the last
        equiv_result = subprocess.run(f"python3 src/equivalence_check.py {log_path} --to_file {temporary_filename} {completeness_check_flags}",
                            shell=True, capture_output=True, text=True)

        # Copy completeness test and append equiv log
        os.rename(temporary_filename, f"{output_dir}/log_{classname}_compl.txt")
        with open(f"{output_dir}/log_{classname}_compl.txt", "a", encoding="utf-8") as equiv_file:
            equiv_file.write(f"\n\n{equiv_result.stdout}\n\n{equiv_result.stderr}\n") 

        if equiv_result.returncode == 0: # Passed equiv test
            # check ground truth
            if equiv_result.returncode == 0:
                ground_truth_filepath = f"dataset_v1_annotated/{classname}.java"
                equiv_ground_truth_result = subprocess.run(f"python3 src/equivalence_check.py {log_path} {ground_truth_filepath} --to_file {temporary_filename} {completeness_check_flags}",
                                shell=True, capture_output=True, text=True)

                os.rename(temporary_filename, f"{output_dir}/log_{classname}_equiv_ground_truth.txt")
                with open(f"{output_dir}/log_{classname}_equiv_ground_truth.txt", "a", encoding="utf-8") as equiv_gt_file:
                    equiv_gt_file.write(f"\n\n{equiv_ground_truth_result.stdout}\n\n{equiv_ground_truth_result.stderr}\n")

    # Copy log
    os.rename(log_path, f"{output_dir}/{log_filename}")

def worker(exp_name, thread_idx, files_chunk, output_dir):
    for filepath in files_chunk:
        classname = os.path.splitext(os.path.basename(filepath))[0]
        tmp_name = f"{classname}_{thread_idx}_tmp.java"
        try:
            process_file(exp_name, filepath, output_dir, tmp_name)
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
        return "-no_check_feas -no_check_null -no_check_arith"
    else:
        return "-no_check_feas"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp",
                        choices=["E1", "E2", "E3", "E4", "E5", "E6", "E7",
                                 "E8", "E9", "E10", "E11", "E12",
                                 "E13", "E14", "E15", "E16", "E17"], required=True)
    args = parser.parse_args()
    exp_name = args.exp

    dataset = list_all_files_os_walk("dataset_v1_no_annotations")

    num_threads = min(NUM_THREADS, len(dataset))

    chunks = split_dataset_n_chunks(dataset, num_threads)

    for i in range(0, NUM_RUNS):

        print(f'run {i}')
        run_dir = f"results_{exp_name}/run_{i}"
        os.makedirs(run_dir, exist_ok=True)

        # Create N threads
        # Each thread will have a chunk
        # Each thread will process all files in the chunk
        # After processing all files from the run, wait until all threads finish
        # Then proceed to next run (outer loop)
        threads = []
        for idx, chunk in enumerate(chunks):
            t = threading.Thread(target=worker, args=(exp_name, idx, chunk, run_dir), name=f"worker-{i}-{idx}")
            t.start()
            threads.append(t)

        # After processing all files from the run, wait until all threads finish
        for t in threads:
            t.join()

    print(f"Finished experiment")
