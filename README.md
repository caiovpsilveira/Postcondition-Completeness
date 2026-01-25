# Assessing Postcondition Completeness in Auto-Generated Function Contracts for Software Verification

**Caio Vinícius Pereira Silveira and Mateus Felipe Tymburibá Ferreira.**

This repository contains the experimental data and source code artifacts.

This is a Proof of Concept implementation done in python.
It does not have a proper Java or JML parser and relies heavily on heuristics to extract those from the source code.

---

## Table of contents

- [Requirements and setup](#requirements-and-setup)
- [Reproducing experiments](#reproducing-experiments)
- [Aggregating results](#aggregating-results)
- [Generating figures](#generating-figures)
- [Documentation](#documentation)
- [Copyright](#copyright)

## Overall File Structure

```
root/
├── dataset_v1_annotated/       # Ground-Truth dataset (oracle)
├── dataset_v1_no_annotations/  # Dataset clean
├── exp_results/                # Our experimental results (logs, CSVs and spreadsheets)
├── figures/                    # Generated plots and figures
├── specgen/                    # Source code and artifacts used from SpecGen
├── src/                        # Source code for this project
├── .gitignore                  # Git ignore file
├── LICENSE                     # MIT license
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

---

## Requirements and setup

```bash
# Python 3.10.12
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

[OpenJML](https://github.com/OpenJML/OpenJML) version [21-0.21](https://github.com/OpenJML/OpenJML/releases/tag/21-0.21).
You will need to add the `openjml` binary path to your `PATH` environment variable.

> If desired, configure your editor to use the new virtual environment at `.venv` to avoid unresolved dependency errors.

> Before invoking any python script, make sure that the virtual environment is active (`source .venv/bin/activate`) in the terminal.

You will need to create a file named `api_key.txt` in the repository root with your OpenAI API key.
> `api_key.txt` is untracked by the git repository to avoid leakage. **Important**: Never commit your API key to version control.

> We used a virtual machine with Ubuntu 22.04 LTS, with 8 dedicated virtualized cores and 16 GB of RAM.
> Consider reducing the parallelism in `src/run_experiments.py` if you have less RAM or cores available. 
> These experiments are not particularly memory hungry. With 16 GB of RAM, you should be able to run even more than 8 threads, depending on how many cores you have.
> If you have 8 GB of total RAM, consider reducing the number of threads to 6 or less.

---

## Reproducing experiments

From the root of the repository, run:
```bash
python src/run_experiments.py --exp EXP
```

`EXP` should be a string E1..E17, corresponding to the experiment name. For more details refer to the paper.

| Model         | SpecGen    | Original Prompt | Strict Prompt | Original Prompt + EC | Strict Prompt + EC |
|---------------|------------|-----------------|---------------|------------------------|----------------------|
| GPT-3.5 turbo | E1 / E3    | E2 / E4         | E5            | E6                     | E7                   |
| GPT-4.1 mini  | E8         | E9              | E10           | E11                    | E12                  |
| GPT-5 mini    | E13        | E14             | E15           | E16                    | E17                  |


After executing, it will create a `results_EXP` directory in the root of your repository.
The `results_EXP` directory contains the log files of all individual tests.

- `log_TEST.txt`: the log of the LLM iterations and mutation attempts. This is always produced.
- `log_TEST_compl.txt`: the log of the external `completeness check`, to classify proven results as Valid vs (Complete/CompleteGT). This is produced for correct results that finished the generation.
- `log_TEST_logical_equiv_GT.txt`: the log of the logical equivalence check against the GT version, to classify complete results as Complete vs Complete GT. This is produced for correct and complete results.

> When running, a `tmp` directory where additional files will be created.
> Do not remove these files until the execution finishes.
> These are moved at the end of the execution for a given test to the `results_EXP` directory.
> **TIP**: To see which tests are running or remaining, you can use `src/get_statistics_from_logs.py`. This will tell which files are missing.

> (Some _SpecGen_ runs can take a while, as they can have 1000+ mutation candidates). By default, it's capped at 1000 mutation iterations, but these tests can take up to 2 hours to run. *Infeasible* in practice, but we were generous with the mutation phase.
> The SpecGen experiments (E1, E3, E8 and E13) might take a while to run, up to ~6 or more hours. The other experiments are quicker, and should finish in around 1h. If desired, reduce the number of max_mutation_iterarions to make the SpecGen experiments quicker, but be aware that this might increase the failure rate.

> The time limits are also *overly conservative*. Each OpenJML call has a time limit of 200s, with the completeness and logical equivalence checks having a time limit of 600s. It's important that the completeness and logical checks have a higher time limit, as they have additional methods to be verified.
> Each test in the dataset is able to be verified with a time limit of 30s of each OpenJML call. 
> Because of that, if some tests appears to be 'stuck', it might be because it's requiring multiple completeness_check invocations. You can check the logs, which should be updated at least once every _completeness_timeout_ seconds.

> If the embedded completeness check is used, `log_TEST_compl.txt` might not exist even if the result is correct.
> This is because the run does not end until a *complete* spec is generated.
> Such cases are still counted as at least _Valid_ by filtering log messages (`src/get_statistics_from_logs.py`).

## Aggregating results

You can then process the `results` directory by calling `python src/get_statistics_from_logs.py RESULTS_DIR`, which will create a pandas dataframe named `experiments_results.csv` in the given `RESULTS_DIR`. This dataframe is also post-processed, marking usage of assumptions, empty postconditions or code modifications as failures.

After that, call `python src/value_analysis.py EXP_RESULTS_CSV`.
It will aggregate the raw dataframe, grouping the results by difficulties and filtering the effects of the mutation and the embedded completeness check.

The result printed from `src/value_analysis.py` was used to create the spreadsheet at `exp_results/Results.ods` (manually).
This spreadsheet is the main data we are interested in.

## Generating figures

To create the figures, refer to `src/stacked_bar_graphics.py` and `src/gen_iterations_boxplot.py`.
You have to manually create two CSVs:

* One CSV with all the overall results `experiment,difficulty,failure,valid,complete,complete_gt`, obtained from `src/value_analysis.py`.
Required for `src/stacked_bar_graphics.py`. It should be placed at `exp_results/grouped_data_classification_only.csv`.
* One CSV with all `experiments_results.csv` combined into a single CSV. Required for `src/gen_iterations_boxplot.py`.
It should be placed at `exp_results/combined_results.csv`.

---

## Documentation

<details open>
<summary><strong>Implementation / running experiments, in order by relevance:</strong></summary>

<br />

`src/run_experiments.py --exp EXP`
This script runs the experiments over all files in the dataset, 10 times each.
It calls `specgen/specgen.py`, which has both the conversational and the SpecGen flow; and after that evaluates the result by inspecting the log file
with the `src/completeness_check.py` and `src/logical_equivalence_check.py` scripts. For each attempt (out of 10) the dataset is parallelized in 8 threads. The result logs (generation loop logs and quality classification logs) are stored in `results` dir at the repo root.
* `--exp EXP` : the experiment name to reproduce. Should be a string E1..E17. For a detailed description of what experiment is, refer to the paper or see `get_experiment_settings()` at `src/run_experiments.py`.

---

`python specgen/specgen.py --input FILE [--key_file FILE] [--max_gen_iterations N] --model MODEL --prompt_type TYPE [--mutation] [--embedded_compl] [--use_nonnull_and_no_ovf_asm]`
This is the script that runs either the _SpecGen_ flow or the plain conversational loop.
* `--input FILE` : the Java source code to try to generate JML specifications for.
* `--key_file FILE` : an optional filepath that contains the OpenAI API key. Defaults to `./api_key.txt`.
* `--max_gen_iterations N` : an optional max_limit of LLM generation attempts. Defaults to 10.
* `--model MODEL` : gpt-3.5-turbo, gpt-4.1-mini, gpt-5-mini
* `--prompt_type TYPE` : original, strict
* `--mutation` : enables the _SpecGen_ workflow. Default is a plain conversational LLM loop, iterating until 'max_gen_iterations' or until proven
* `--embedded_compl` : enables integrating the *completeness check* in the feedback loop. Iterates until 'max_gen_iterations' or until proven and complete.
* `--use_nonnull_and_no_ovf_asm` : uses OpenJML switches to assume always valid references and absence of arithmetic overflow (Ma et al. original setup). Default is off.

---

`python src/completeness_check.py SOURCE_FILE [-no_check_null] [-no_check_arith] --to_file FILE`
This is the completeness check. The main method is `check_completeness`. It creates a new test file,
copies the methods body and specifications, adds an auxiliary `test_completeness` method and runs OpenJML.
The file provided as a parameter should either be a Java source file with JML specifications, or the log from `specgen.py`, in which case
it will get the latest attempt (delimited by the Java class).
* `SOURCE_FILE` : the Java source file with JML annotations or log to be checked.
* `-no_check_null` : uses assumptions of always valid references with OpenJML: `--nonnull-by-default`. If unspecified, it uses `--nullable-by-default`.
* `-no_check_arith` : uses assumptions that arithmetic overflow cannot happen with OpenJML: `--arithmetic-failure=quiet`.
* `--to_file FILE` : specifies the filename in which the checks will be performed. This file needs to be created to invoke OpenJML on it. This parameter allows for parallelizing the dataset.

<details closed>
<summary><strong>[Expand] Completeness check example</strong></summary>

Copy the following contents to a Java file `Calc.java`.

First, check if it's verified with OpenJML:
`openjml --esc --nullable-by-default --timeout 30 --progress Calc.java`
Now run `python src/completeness_check.py Calc.java --to_file Test.java`

```java
public class Calc {
    //@  requires op == '+'
    //@  requires Integer.MIN_VALUE <= a + b <= Integer.MAX_VALUE;
    //@  assigns \nothing;
    //@  ensures \result == a + b;
    //@ also
    //@  requires op == '-'
    //@  requires Integer.MIN_VALUE <= a - b <= Integer.MAX_VALUE;
    //@  assigns \nothing;
    //@  ensures \result == a - b;
    public static int calc(int a, int b, char op) {
        if (op == '+') {
            return a + b;
        } else if (op == '-') {
            return a - b;
        }
    }
}
```
Now change `Calc.java` to be the following:
This is not complete, because it does not capture the implication of the operator value.

First, check if it's verified with OpenJML:
`openjml --esc --nullable-by-default --timeout 30 --progress Calc.java`
Now run `python src/completeness_check.py Calc.java --to_file Test.java`
```java
public class Calc {
    //@  requires op == '+' || op == '-';
    //@  requires Integer.MIN_VALUE <= a + b <= Integer.MAX_VALUE;
    //@  requires Integer.MIN_VALUE <= a - b <= Integer.MAX_VALUE;
    //@  assigns \nothing;
    //@  ensures \result == a + b || \result == a - b;
    public static int calc(int a, int b, char op) {
        if (op == '+') {
            return a + b;
        } else if (op == '-') {
            return a - b;
        }
    }
}
```
</details>

The completeness check relies on a library that provides overloads for methods `T DeepCopy(T a)` and `boolean Equals(T a, T b)`.
These overloads are required to ensure that for references, a deep copy will be performed and that we will compare only the effective content,
not reference values.

The library specification is available in `src/completeness/util/CompletenessUtil.jml` and the implementation (for validating the specs) is available on `src/completeness/util/CompletenessUtil.java`.

---

`python src/logical_equivalence_check.py SOURCE_FILE1 SOURCE_FILE2 [-no_check_null] [-no_check_arith] --to_file FILE`
This is the script that checks the logical equivalence of methods with JML annotations in two Java files (or logs).
The main method is `check_logical_equivalence`. It creates a new test file, copies the method body and specification, adds auxiliary methods and runs OpenJML.

* `SOURCE_FILE1` : the first file to be checked
* `SOURCE_FILE2` : the second file to be checked.
* `-no_check_null` : uses assumptions of always valid references with OpenJML: `--nonnull-by-default`. If unspecified, it uses `--nullable-by-default`.
* `-no_check_arith` : uses assumptions that arithmetic overflow cannot happen with OpenJML: `--arithmetic-failure=quiet`.
* `--to_file FILE` : specifies the filename in which the checks will be performed. This file needs to be created to invoke OpenJML on it. This parameter allows for parallelizing the dataset.

<details closed>
<summary><strong>[Expand] Logical equivalence check example</strong></summary>

Copy contents below to two Java files: `Abs1.java` and `Abs2.java`

Abs1.java:
```java
public class Abs1
{
    //@ requires x != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //@ ensures \result == (x > 0 ? x : -x);
    public static int abs(int x) {
        return x > 0 ? x : -x;
    }
}
```
Abs2.java:
```java
public class Abs2
{
    //@ requires x != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //@ ensures \result >= 0;
    //@ ensures \result == x || \result == -x;
    public static int abs(int x) {
        return x > 0 ? x : -x;
    }
}
```
The specifications above are logically equivalent specifications.
First, check if it's verified with OpenJML:
`openjml --esc --nullable-by-default --timeout 30 --progress Abs1.java`
`openjml --esc --nullable-by-default --timeout 30 --progress Abs2.java`
Now run `python src/logical_equivalence_check.py Abs1.java Abs2.java --to_file Test.java`

Now change `Abs2.java` to:
```java
public class Abs2
{
    //@ requires x != Integer.MIN_VALUE;
    //@ assigns \nothing;
    //@ ensures \result >= 0;
    public static int abs(int x) {
        return x > 0 ? x : -x;
    }
}
```

`Abs2.java` postcondition is now not-equivalent to `Abs1.java` postcondition.
First, check if it's verified with OpenJML:
`openjml --esc --nullable-by-default --timeout 30 --progress Abs1.java`
`openjml --esc --nullable-by-default --timeout 30 --progress Abs2.java`
Now run `python src/logical_equivalence_check.py Abs1.java Abs2.java --to_file Test.java`

Now change `Abs2.java` to:
Abs2.java:
```java
public class Abs2
{
    //@ requires x >= 0;
    //@ assigns \nothing;
    //@ ensures \result >= 0;
    //@ ensures \result == x || \result == -x;
    public static int abs(int x) {
        return x > 0 ? x : -x;
    }
}
```

`Abs2.java` precondition is now not-equivalent to `Abs1.java` precondition.
First, check if it's verified with OpenJML:
`openjml --esc --nullable-by-default --timeout 30 --progress Abs1.java`
`openjml --esc --nullable-by-default --timeout 30 --progress Abs2.java`
Now run `python src/logical_equivalence_check.py Abs1.java Abs2.java --to_file Test.java`
</details>

---

`python src/file_processor.py SOURCE_FILE`
This is a "parser", that reads a source code or the log, gets the code of the last attempt generated and creates an auxiliary data structure, list\[MethodSpecification]. The main method is `process_file`.
* `SOURCE_FILE` : A Java source file or a log file generated from `specgen/specgen.py`, in which case it will get the last `class` body in the log.

</details>

<details open>
<summary><strong>Get experimental data:</strong></summary>

<br />

`src/get_statistics_from_logs.py RESULTS_DIR`
This script processes all of the logs under `results` (obtained after `src/run_experiments.py`) and creates a pandas dataset with the result type and other metrics, one for each test x run. It also does a post-processing, invalidating attempts that had the code modified, used assumptions or had empty postconditions. The dataframe is exported in `RESULTS_DIR/experiments_results.csv`.

`src/value_analysis.py EXP_RESULTS_CSV`
This script groups all of the results in the dataframe obtained from `src/get_statistics_from_logs.py`. It then prints this information in the stdout, which can be copied and pasted into a spreadsheet (like what we did for `exp_results/Results.ods`.)

</details>

<details open>
<summary><strong>Generate figures:</strong></summary>

<br />

`src/stacked_bar_graphics.py`
This script creates the 100% stacked bar figures. It requires a `exp_results/grouped_data_classification_only.csv`, which needs to be manually created with the data from `src/value_analysis.py`. It will create one figure for each possible comparison. The figures are saved to the `figures` directory. In the paper, we choose a few only because of limited size.

`src/gen_iterations_boxplot.py`
This script creates the generation iterations boxplot. It will create one for each difficulty, gathering all tests data. It requires a `exp_results/combined_results.csv`, which needs to be manually created by grouping the dataframes obtained from `src/get_statistics_from_logs.py`. The figures are saved to the `figures` directory.

</details>

---

## Copyright
### SpecGen sourced files
The files under the `specgen` directory were directly sourced or modified from the original [SpecGen](https://doi.org/10.1109/ICSE55347.2025.00129) artifact repository:
* Upstream: https://github.com/Lezhi-Ma/SpecGen-Artifact
* Fork (no changes): https://github.com/caiovpsilveira/SpecGen-Artifact

These files are licensed under the MIT License. Copyright Lezhi Ma and contributors.

The major changes are in `spegcen/specgen.py` and for the feedback, either in the `specgen/refinement_prompt.py` or in the `specgen/prompts/refine/`.
These were giving feedback suggesting usage of assumptions, which is undesired.

### Dataset
The dataset is a mix of common computer science tasks and algorithms, sourced from [SpecGenBench](https://github.com/Lezhi-Ma/SpecGen-Artifact), [CloverBench](https://github.com/ChuyueSun/Clover), [LeetCode tasks](https://github.com/fluency03/leetcode-java/) and mixed sources.

The JML annotations were mannually added and verified for correctness and completeness by Caio Vinícius Pereira Silveira.

### Remaining files
The remaining files are distributed under the MIT license. Copyright Caio Vinícius Pereira Silveira.
