from pathlib import Path
import subprocess
import tempfile
import tqdm

def check_java_compiler(dataset_annotated_path, dataset_no_annotations_path):

    java_files = list(dataset_annotated_path.glob('**/*.java')) + list(dataset_no_annotations_path.glob('**/*.java'))

    with tempfile.TemporaryDirectory() as tmpdir:
        for java_file in tqdm.tqdm(java_files, desc="Compiling Java files"):
            result = subprocess.run(
                ["javac", "-d", tmpdir, str(java_file)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"[FAIL] javac {java_file}")
                # if result.stdout:
                #     print(result.stdout)
                # if result.stderr:
                #     print(result.stderr)
            else:
                #print(f"[OK] {java_file}")
                pass

def check_removed_annotations(dataset_no_annotations_path):
    java_files = list(dataset_no_annotations_path.glob('**/*.java'))
    
    for java_file in tqdm.tqdm(java_files, desc="Checking removed annotations"):
        with open(java_file, 'r') as f:
            content = f.read()
            if '//@' in content or '/*@' in content or '@*/' in content:
                print(f"[FAIL] annotations not removed in {java_file}")
            else:
                #print(f"[OK] {java_file}")
                pass

def check_openjml(dataset_annotated_path):
    java_files = list(dataset_annotated_path.glob('**/*.java'))

    # openjml --esc --esc-max-warnings 1 --nullable-by-default --arithmetic-failure=hard --timeout 30 --progress

    for java_file in tqdm.tqdm(java_files, desc="Checking OpenJML"):
        result = subprocess.run(
            ["openjml", "--esc", "--esc-max-warnings", "1", "--nullable-by-default", "--arithmetic-failure=hard", "--timeout", "30", "--progress", str(java_file)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[FAIL] openjml {java_file}")
            # if result.stdout:
            #     print(result.stdout)
            # if result.stderr:
            #     print(result.stderr)
        else:
            #print(f"[OK] {java_file}")
            pass

def check_logical_equivalence(dataset_annotated_path):
    java_files = list(dataset_annotated_path.glob('**/*.java'))

    # python src/logical_equivalence_check.py file file --to_file tmp_file

    for java_file in tqdm.tqdm(java_files, desc="Checking logical equivalence"):
        with tempfile.NamedTemporaryFile(suffix='.java', delete=True) as tmp_file:
            result = subprocess.run(
                ["python", "src/logical_equivalence_check.py", str(java_file), str(java_file), "--to_file", tmp_file.name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"[FAIL] logical equivalence {java_file}")
                # if result.stdout:
                #     print(result.stdout)
                # if result.stderr:
                #     print(result.stderr)
            else:
                #print(f"[OK] {java_file}")
                pass

def check_completeness(dataset_annotated_path):
    java_files = list(dataset_annotated_path.glob('**/*.java'))

    # python src/completeness_check.py file --to_file tmp_file
    
    for java_file in tqdm.tqdm(java_files, desc="Checking completeness"):
        with tempfile.NamedTemporaryFile(suffix='.java', delete=True) as tmp_file:
            result = subprocess.run(
                ["python", "src/completeness_check.py", str(java_file), "--to_file", tmp_file.name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"[FAIL] completeness {java_file}")
                # if result.stdout:
                #     print(result.stdout)
                # if result.stderr:
                #     print(result.stderr)
            else:
                #print(f"[OK] {java_file}")
                pass

if __name__ == "__main__":
    dataset_annotated_path = Path('dataset_v1_annotated')
    dataset_no_annotations_path = Path('dataset_v1_no_annotations')
    check_java_compiler(dataset_annotated_path, dataset_no_annotations_path)
    check_removed_annotations(dataset_no_annotations_path)
    check_openjml(dataset_annotated_path)
    check_logical_equivalence(dataset_annotated_path)
    check_completeness(dataset_annotated_path)
