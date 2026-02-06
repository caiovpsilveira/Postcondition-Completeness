from pathlib import Path
import subprocess
import tempfile
import tqdm
import sys

def check_java_compiler(dataset_annotated_path, dataset_no_annotations_path):
    all_succeed = True

    java_files = list(dataset_annotated_path.glob('**/*.java')) + list(dataset_no_annotations_path.glob('**/*.java'))

    with tempfile.TemporaryDirectory() as tmpdir:
        for java_file in tqdm.tqdm(java_files, desc="Checking Java compiler"):
            result = subprocess.run(
                ["javac", "-d", tmpdir, str(java_file)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                all_succeed = False
                print(f"[FAIL] javac {java_file}")
                # if result.stdout:
                #     print(result.stdout)
                # if result.stderr:
                #     print(result.stderr)
            else:
                #print(f"[OK] {java_file}")
                pass

    return all_succeed

def check_removed_annotations(dataset_no_annotations_path):
    all_succeed = True

    java_files = list(dataset_no_annotations_path.glob('**/*.java'))
    
    for java_file in tqdm.tqdm(java_files, desc="Checking removed annotations"):
        with open(java_file, 'r') as f:
            content = f.read()
            if '//@' in content or '/*@' in content or '@*/' in content:
                all_succeed = False
                print(f"[FAIL] annotations not removed in {java_file}")
            else:
                #print(f"[OK] {java_file}")
                pass

    return all_succeed

def check_openjml(dataset_annotated_path):
    all_succeed = True

    java_files = list(dataset_annotated_path.glob('**/*.java'))

    # openjml --esc --esc-max-warnings 1 --nullable-by-default --arithmetic-failure=hard --timeout 30 --progress

    for java_file in tqdm.tqdm(java_files, desc="Checking OpenJML"):
        result = subprocess.run(
            ["openjml", "--esc", "--esc-max-warnings", "1", "--nullable-by-default", "--arithmetic-failure=hard", "--timeout", "30", "--progress", str(java_file)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            all_succeed = False
            print(f"[FAIL] openjml {java_file}")
            # if result.stdout:
            #     print(result.stdout)
            # if result.stderr:
            #     print(result.stderr)
        else:
            #print(f"[OK] {java_file}")
            pass

    return all_succeed

def check_self_logical_equivalence(dataset_annotated_path):
    all_succeed = True

    java_files = list(dataset_annotated_path.glob('**/*.java'))

    # python src/logical_equivalence_check.py file file --to_file tmp_file

    for java_file in tqdm.tqdm(java_files, desc="Checking self logical equivalence on dataset annotated"):
        with tempfile.NamedTemporaryFile(suffix='.java', delete=True) as tmp_file:
            result = subprocess.run(
                ["python", "src/logical_equivalence_check.py", str(java_file), str(java_file), "--to_file", tmp_file.name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                all_succeed = False
                print(f"[FAIL] self logical equivalence {java_file}")
                # if result.stdout:
                #     print(result.stdout)
                # if result.stderr:
                #     print(result.stderr)
            else:
                #print(f"[OK] {java_file}")
                pass

    return all_succeed

def check_equivalent_samples():
    eqv_samples_dir = Path('tests/equivalent_samples')
    equivalent_samples = [
                            [f'{eqv_samples_dir}/Abs1_1.java', f'{eqv_samples_dir}/Abs1_2.java'],
                            [f'{eqv_samples_dir}/IsPrefix_1.java', f'{eqv_samples_dir}/IsPrefix_2.java']
                        ]

    all_succeed = True

    for pair in tqdm.tqdm(equivalent_samples, desc="Checking equivalent samples"):
        file1 = pair[0]
        file2 = pair[1]

        with tempfile.NamedTemporaryFile(suffix='.java', delete=True) as tmp_file:
            result = subprocess.run(
                ["python", "src/logical_equivalence_check.py", str(file1), str(file2), "--to_file", tmp_file.name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                all_succeed = False
                print(f"[FAIL] logical equivalence {file1} and {file2} (were reported as non-equivalent)")
                # if result.stdout:
                #     print(result.stdout)
                # if result.stderr:
                #     print(result.stderr)
            else:
                #print(f"[OK] {file1} and {file2}")
                pass

    return all_succeed

def check_non_equivalent_samples():
    non_equivalent_dir = Path('tests/non_equivalent_samples')
    non_equivalent_samples = [
                            [f'{non_equivalent_dir}/Abs1_1.java', f'{non_equivalent_dir}/Abs1_2.java']
                        ]

    all_succeed = True

    for pair in tqdm.tqdm(non_equivalent_samples, desc="Checking non-equivalent samples"):
        file1 = pair[0]
        file2 = pair[1]
        with tempfile.NamedTemporaryFile(suffix='.java', delete=True) as tmp_file:

            result = subprocess.run(
                ["python", "src/logical_equivalence_check.py", str(file1), str(file2), "--to_file", tmp_file.name],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                all_succeed = False
                print(f"[FAIL] non-equivalence {file1} and {file2} (were reported as equivalent)")
                # if result.stdout:
                #     print(result.stdout)
                # if result.stderr:
                #     print(result.stderr)
            else:
                #print(f"[OK] {file1} and {file2}")
                pass

    return all_succeed

def check_completeness(dataset_annotated_path):
    all_succeed = True

    java_files = list(dataset_annotated_path.glob('**/*.java'))

    # python src/completeness_check.py file --to_file tmp_file
    
    for java_file in tqdm.tqdm(java_files, desc="Checking completeness on dataset annotated"):
        with tempfile.NamedTemporaryFile(suffix='.java', delete=True) as tmp_file:
            result = subprocess.run(
                ["python", "src/completeness_check.py", str(java_file), "--to_file", tmp_file.name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                all_succeed = False
                print(f"[FAIL] completeness {java_file}")
                # if result.stdout:
                #     print(result.stdout)
                # if result.stderr:
                #     print(result.stderr)
            else:
                #print(f"[OK] {java_file}")
                pass

    return all_succeed

def check_incomplete_samples():
    incomplete_samples_path = Path('tests/incomplete_samples')

    java_files = list(incomplete_samples_path.glob('**/*.java'))

    all_succeed = True

    for java_file in tqdm.tqdm(java_files, desc="Checking incomplete samples"):
        with tempfile.NamedTemporaryFile(suffix='.java', delete=True) as tmp_file:
            result = subprocess.run(
                ["python", "src/completeness_check.py", str(java_file), "--to_file", tmp_file.name],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                all_succeed = False
                print(f"[FAIL] incomplete sample marked as complete {java_file}")
                # if result.stdout:
                #     print(result.stdout)
                # if result.stderr:
                #     print(result.stderr)
            else:
                #print(f"[OK] {java_file}")
                pass

    return all_succeed

if __name__ == "__main__":
    dataset_annotated_path = Path('dataset_v1_annotated')
    dataset_no_annotations_path = Path('dataset_v1_no_annotations')

    all_succeed = True
    all_succeed &= check_java_compiler(dataset_annotated_path, dataset_no_annotations_path)
    all_succeed &= check_removed_annotations(dataset_no_annotations_path)
    all_succeed &= check_openjml(dataset_annotated_path)
    all_succeed &= check_self_logical_equivalence(dataset_annotated_path)
    all_succeed &= check_equivalent_samples()
    all_succeed &= check_non_equivalent_samples()
    all_succeed &= check_completeness(dataset_annotated_path)
    all_succeed &= check_incomplete_samples()

    if all_succeed:
        print("All sanity checks passed!")
        sys.exit(0)
    else:
        print("Some sanity checks failed. Refer to the stdout for details.")
        sys.exit(1)
