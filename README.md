# Assessing Postcondition Completeness in Auto-Generated Function Contracts for Software Verification

**Caio Vinícius Pereira Silveira and Mateus Felipe Tymburibá Ferreira.**

This repository contains the experimental data and source code artifacts.

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

[OpenJML](https://github.com/OpenJML/OpenJML) version [21-0-17](https://github.com/OpenJML/OpenJML/releases/tag/21-0.17).
You will need to add the `openjml` binary path to your `PATH` environment variable.

> If desired, configure your editor to use the new virtual environment at `.venv` to avoid unresolved dependency errors.

> Before invoking any python script, make sure that the virtual environment is active (`source .venv/bin/activate`) in the terminal.

You will need to create a file named `api_key.txt` in the repository root with your OpenAI API key.
> `api_key.txt` is untracked by the git repository to avoid leakage. **Important**: Never commit your API key to version control.

> We used a virtual machine with Ubuntu 22.04 LTS, with 8 dedicated virtualized cores and 16 GB of RAM.
> Consider reducing the parallelism in `src/run_experiments.py` if you have less RAM or cores available. 

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
- `log_TEST_equiv.txt`: the log of the external `completeness check`, to classify proven results as Valid vs (Complete/CompleteGT). This is produced for correct results that finished the generation.
- `log_TEST_equiv_ground_truth.txt`: the log of the logical equivalence check against the GT version, to classify complete results as Complete vs Complete GT. This is produced for correct and complete results.

> When running, a `tmp` and `logs` directory and some additional files will be created to the root of the repository.
> Do not remove these files until the execution finishes.
> These are moved at the end of the execution for a given test to the `results_EXP` directory.
> To see what tests are running, see the `logs` directory.
> (Some _SpecGen_ runs can take a while, as they can have 600+ mutation candidates).

> If the embedded completeness check is used, `log_TEST_equiv.txt` might not exist even if the result is correct.
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
with the `equivalence_check.py` script. For each attempt (out of 10) the dataset is parallelized in 8 threads. The result logs (generation loop logs and quality classification logs) are stored in `results` dir at the repo root.
* `--exp EXP` : the experiment name to reproduce. Should be a string E1..E17. For a detailed description of what experiment is, refer to the paper or see `get_experiment_settings()` at `src/run_experiments.py`.

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

`python src/equivalence_check.py SOURCE_FILE1 [SOURCE_FILE2] [-no_check_feas] [-no_check_null] [-no_check_arith] --to_file FILE`
This is the script that checks two things: the *completeness check* and the *logical equivalence check*.
The main method is `check_equivalence`. It creates a new test file, copies the method body and specification, adds auxiliary methods and runs OpenJML.
It receives two files as a parameter. If you specify the same file, it will do the `completeness check` (as it is logically equivalent to itself).
If you specify two different files, it will check if the preconditions are `logically equivalent` and will perform the `completeness check`.
In summary: pass a single file to do the completeness check, pass the file and the oracle (dataset_v1_annotated) to do the logical equivalence check.

* `SOURCE_FILE1` : the first file to be checked
* `SOURCE_FILE2` : an optional second file to be checked. If omitted, the script will check `SOURCE_FILE1` against itself.
* `-no_check_feas` : disables the OpenJML `--check_feasibility=all` switch (changes to `--check_feasibility=none`).
* `-no_check_null` : uses assumptions of always valid references with OpenJML: `--nonnull-by-default`. If unspecified, it uses `--nullable-by-default`.
* `-no_check_arith` : uses assumptions that arithmetic overflow cannot happen with OpenJML: `--arithmetic-failure=quiet`.
* `--to_file FILE` : specifies the filename in which the checks will be performed. This file needs to be created to invoke OpenJML on it. This parameter allows for parallelizing the dataset.

> Why our tests have -no_check_feas (--check_feasibility=none)
> --check_feasibility is an OpenJML switch that can check multiple things, such as unreachable code (Refer to the User Guide [documentation](https://www.openjml.org/documentation/)).
> When I was experimenting, I decided to try with (--check_feasibility=all) to verify that the preconditions were not constraining any relevant part of the code.
> However, I got some issues, where OpenJML was pointing --check_feasibility failures in weird parts, such as the end of the Java class (like 2nd example in [#888](https://github.com/OpenJML/OpenJML/issues/888)).
> For that reason, I decided to not enable it.
> Later David R. Cok suggested using only --check_feasibility=basic, but I had already run some of the experiments.

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

### Remaining files
The remaining files are distributed under the MIT license. Copyright Caio Vinícius Pereira Silveira.
