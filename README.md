# Assessing Postcondition Completeness in Auto-Generated Function Contracts for Software Verification

**Anonymized author(s)**

This repository contains the experimental data and source code artifacts.

This is a Proof of Concept implementation done in python.
It does not have a proper Java or JML parser and relies heavily on heuristics to extract those from the source code.

---

## Table of contents

- [Requirements and setup](#requirements-and-setup)
- [Reproducing - Quick Start](#reproducing)
- [Reproducing experiments](#reproducing-experiments)
- [Aggregating results](#aggregating-and-reporting-results)
- [Generating figures](#generating-figures)
- [The completeness util library](#the-completeness-util-library)
- [Copyright](#copyright)

## Overall File Structure

```
proj_root/
├── all_results/                           # Our experimental results (logs, CSVs and spreadsheets)
├── dataset_v1_annotated/                  # Ground-Truth dataset (oracle)
├── dataset_v1_no_annotations/             # Dataset clean
├── dataset_v1_annotated_incomplete_specs/ # Ground-Truth dataset with some behaviors removed
├── figures/                               # Generated plots and figures
├── old_figures/                           # Generated plots and figures - old experiment names
├── renamed_results_src                    # Scripts to generate the figures for the exps. we want to present. See PAPER NOTICE
├── FormalBench_mutation_analysis          # Mutation-Based completeness verification artifacts
├── specgen/                               # Source code and artifacts used from SpecGen
├── src/                                   # Source code for this project
├── tests/                                 # Test files for the completeness and equivalence scripts
├── .gitignore                             # Git ignore file
├── LICENSE                                # MIT license
├── README.md                              # Project documentation
├── requirements.txt                       # Python (3.10.12) dependencies
└── run_tests.py                           # Sanity script to see if the setup, dataset and scripts are running as expected
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

```bash
python --version
> Python 3.10.12
which openjml
> /your/path/openjml
openjml --version
> openjml 21-0.21
```

> If desired, configure your editor to use the new virtual environment at `.venv` to avoid unresolved dependency errors.

> Before invoking any python script, make sure that the virtual environment is active (`source .venv/bin/activate`) in the terminal.

You will need to create a file named `api_key.txt` in the repository root with your OpenAI API key.
> `api_key.txt` is untracked by the git repository to avoid leakage. **Important**: Never commit your API key to version control.

> We used a machine with Ubuntu 22.04 LTS with 16 cores and 32 GB of RAM, using 8 cores for parallelism.
> Consider reducing the parallelism in `src/run_experiments.py` if you have less RAM or cores available. 
> These experiments are not particularly memory hungry. With 16 GB of RAM, you should be able to run even more than 8 threads, depending on how many cores you have.
> If you have less than 16 GB of total RAM, consider reducing the number of threads to 6 or less.

After doing the setup, run the following sanity check. It will take a while. It should print "All sanity checks passed!" at the end.
```bash
python run_tests.py
```

---
## Reproducing

Quick overview:
```bash
mkdir my_all_results
for NUM in {1..17}; do
    python src/run_experiments.py --exp E${NUM} | tee E${NUM}_stdout.txt
    mv E${NUM}_stdout.txt results_E${NUM}
    mv results_E${NUM} my_all_results
done
python src/get_statistics_from_logs.py my_all_results
python src/value_analysis.py my_all_results
python src/stacked_bar_graphics.py my_all_results
python src/gen_iterations_boxplot.py my_all_results
./figures/replace_figures.sh
```

## Reproducing experiments

From the root of the repository (with the virtual environment), run:
```bash
python src/run_experiments.py --exp EXP
```

`EXP` should be a string E1..E17, corresponding to the experiment name. For more details refer to the paper.

| Model         | SpecGen    | Original Prompt | Strict Prompt | Original Prompt + EC   | Strict Prompt + EC   |
|---------------|------------|-----------------|---------------|------------------------|----------------------|
| GPT-3.5 turbo | E1 / E3    | E2 / E4         | E5            | E6                     | E7                   |
| GPT-4.1 mini  | E8         | E9              | E10           | E11                    | E12                  |
| GPT-5 mini    | E13        | E14             | E15           | E16                    | E17                  |


PAPER NOTICE: for the paper submission, we choose to don't present the results of comparing different generation prompts and from running _with_ non-null and no-overflow assumptions (as in Ma et al. evaluation).
We ran experiments comparing the original generation prompt against a prompt with more strict generation rules (See specgen/prompt_format.py).
The results were inconclusive, with a bit more better results towards the strit prompt.
Due to the paper size and the low significance of these results, we decided to keep them out of the paper.
For the reader continuity, we renamed the remaining experiments presented.
Experiments E1 and E2 have the non-null and no-overflow assumptions.
Experiments E5, E7, E10, E12, E15 and E17 are the strict prompt experiments.
The all_results contains the original data. The "renamed_results" still refers to the original data, but renames when plotting.

The mapping from the actual experiment setting to the one displayed on the paper:
E3 -> E1; E4 -> E2; E6 -> E3; E8 -> E4; E9 -> E5; E11 -> E6; E13 -> E7; E14 -> E8; E16 -> E9.

Or, coming from the paper, the mapping of the displayed experiment to the actual experiment setting:
E1 -> E3; E2 -> E4; E3 -> E6; E4 -> E8; E5 -> E9; E6 -> E11; E7 -> E13; E8 -> E14; E9 -> E16

See renamed_results_src/ dir. It's a copy-adapted version of the figures scripts under src.

Paper table:
| Model         | SpecGen    | Conversational  | Conversational + EC |
|---------------|------------|-----------------|---------------------|
| GPT-3.5 turbo | E1         | E2              | E3                  |
| GPT-4.1 mini  | E4         | E5              | E6                  |
| GPT-5 mini    | E7         | E8              | E9                  |



After executing, it will create a `results_EXP` directory in the root of your repository.
The `results_EXP` directory contains the log files of all individual tests, one for each (0..9) runs.

- `log_TEST.txt`: the log of the LLM iterations and mutation attempts. This is always produced.
- `log_TEST_compl.txt`: the log of the external `completeness check`, to classify proven results as Valid vs (Complete/CompleteGT). This is produced for correct results that finished the generation.
- `log_TEST_logical_equiv_GT.txt`: the log of the logical equivalence check against the GT version, to classify complete results as Complete vs Complete GT. This is produced for correct and complete results.

> When running, a `tmp` directory is created where additional files will be stored.
> Do not remove these files until the execution finishes.
> These files are temporary working artifacts used during execution and are cleaned up at the end of the experiment run.
> **TIP**: To see which tests are running or remaining, you can use `src/get_statistics_from_logs.py results_EXP`. This will tell which files are missing.

> (Some _SpecGen_ runs can take a while, as they can have 1000+ mutation candidates). By default, it's capped at 1000 mutation iterations, but these tests can take up to 2 hours to run. *Infeasible* in practice, but we were generous with the mutation phase.
> The SpecGen experiments (E1, E3, E8 and E13) might take a while to run, up to ~6 or more hours. The other experiments are quicker, and should finish in around 1h. If desired, reduce the number of max_mutation_iterations to make the SpecGen experiments quicker, but be aware that this might increase the failure rate.

> The time limits are also *overly conservative*. Each OpenJML call has a time limit of 200s, with the completeness and logical equivalence checks having a time limit of 600s. It's important that the completeness and logical checks have a slightly higher time limit, as they have additional methods to be verified.
> Each test in the dataset is able to be verified with a time limit of 30s of each OpenJML call. 
> Because of that, if some tests appears to be 'stuck', it might be because it's requiring multiple completeness_check invocations. You can check the logs, which should be updated at least once every _completeness_timeout_ seconds.

> If the embedded completeness check is used, `log_TEST_compl.txt` might not exist even if the result is correct.
> This is because the run does not end until a *complete* spec is generated.
> Such cases are still counted as at least _Valid_ by filtering log messages (`src/get_statistics_from_logs.py`).

## Aggregating and reporting results

Note: both the commands below can be used in a single `results_EXP` directory, or in a parent directory (all_results) with all 17 `results_EXP` under it.

By calling `python src/get_statistics_from_logs.py DIR`, it will create a CSV named `experiments_results.csv` (for individual experiment) or `combined_results.csv` (for parent directory) in the given `DIR`. This dataframe is also post-processed, marking usage of assumptions, empty postconditions or code modifications as failures.

After that, call `python src/value_analysis.py DIR`.

This will produce the following files under `DIR`:
* `experiments_results.csv` or `combined_results.csv`: A CSV containing individual run x test for all experiments.
* `completeness.csv`: the csv containing how many times the embedded_completeness was activated, and the result outcome (only relevant for E6, E7, E11, E12, E16 and E17), grouped by {experiment, difficulty}.
* `grouped_data_classification_only.csv`: this csv aggregates all individual (run x test) results and groups them by {experiment, difficulty}.
* `mutation.csv`: the csv containing how many times the specgen mutation was activated, and the result outcome (only relevant for E1, E3, E8 and E13), grouped by {experiment, difficulty}.
* `overall_results.csv`: this csv aggregates all individual (run x test) results and groups them by experiment.
* `overall_time_avg.csv`: this csv aggregates all individual (run x test) time and groups them by experiment.
* `time_avg_per_difficulty.csv`: this csv aggregates all individual (run x test) time and groups them by {experiment, difficulty}.

The files created from `src/value_analysis.py` were used to create the spreadsheet at `all_results/ResultsSpreadsheet.ods` (manually).
This spreadsheet is the end data we are interested in.

## Generating figures

To create the stacked bar graphics, use `python src/stacked_bar_graphics.py my_all_results`.
This requires a parent directory with all `results_EXP` under it, as it compares different results.
This will output the PDFs of the comparisons discussed in the paper.

To create the iterations x result boxplot, use `python src/gen_iterations_boxplot.py my_all_results`.
This requires a parent directory with all `results_EXP` under it, as it contains data from all experiments.
This will output the PDFs of the boxplots discussed in the paper.

After generating the figures, call `./figures/replace_figures.sh`, to move the figures to the corresponding directory and replace the old ones.
figures/ contains the following subdirectories:
* changes_across_models: figures comparing gpt 3.5 turbo x gpt 4.1 mini x gpt 5 mini on the same experiment setup.
* flowcharts: PDFs of the flowcharts for SpecGen and the Embedded Completeness check.
* gen_iterations_boxplot: figures of the boxplots of the difficulty x number of gen iterations per result.
* impact_arith_non_null: figures comparing the effect of removing non_null_by_default and arithmetic_failure=quiet.
* impact_embedded_completeness: figures comparing the overall results of having the embedded completeness check with the same experiment setup.
* impact_mutation: figures comparing having the SpecGen mutation vs the plain LLM conversational loop with the same experiment setup.
* prompt_influence: figures comparing the original SpecGen prompt and the stricter prompt, for the same experiment setup.
* reproduce: figures of reproducing the results for the Ma. et al. experiments (GPT-3.5 turbo, original prompt, assumptions, SpecGen x plain conversational).

## The completeness util library

The completeness check uses an auxiliary library that provides the DeepCopy and Equals methods for the dataset types.
These are available under `src/completeness`.

The specification file (.jml) and the Java bytecode (.class) is in `src/completeness/util`. This is what OpenJML uses.

The implementation in `src/completeness/CompletenessUtil.java` has already been verified. It is hidden from OpenJML during test runs to prevent redundant verification and save time.

---

## Copyright
### SpecGen sourced files
The files under the `specgen` directory were directly sourced or modified from the original [SpecGen](https://doi.org/10.1109/ICSE55347.2025.00129) artifact repository:
* Upstream: https://github.com/Lezhi-Ma/SpecGen-Artifact (c7e57445a66dd432d1b9605092d0386455ed3df5)

These files are licensed under the MIT License. Copyright Lezhi Ma and contributors.

The major changes are in `specgen/specgen.py` and for the feedback, either in the `specgen/refinement_prompt.py` or in the `specgen/prompts/refine/`.
These were giving feedback suggesting usage of assumptions, which is undesired.

### Dataset
The dataset is a mix of common computer science tasks and algorithms, sourced from [SpecGenBench](https://github.com/Lezhi-Ma/SpecGen-Artifact), [CloverBench](https://github.com/ChuyueSun/Clover), [LeetCode tasks](https://github.com/fluency03/leetcode-java/) and mixed sources.

The JML annotations were manually added and verified for correctness and completeness by Anonymized author(s).

### Remaining files
The remaining files are distributed under the MIT license. Copyright Anonymized author(s).
