import pandas as pd
import argparse
import os
import re
from typing import List


COMBINED_RESULTS_COLUMNS = [
    'experiment',
    'run',
    'difficulty',
    'classname',
    'result',
    'time',
    'number_of_iterations_before_first_correct',
    'number_of_gen_iterations',
    'number_of_mut_iterations',
    'llm_gave_up',
    'had_embedded_compl_check',
]

PRELIMINARY_DATASET = {
    "easy/Abs1.java",
    "easy/Abs2.java",
    "easy/Avg1.java",
    "easy/Avg2.java",
    "easy/Calculator1.java",
    "easy/Calculator2.java",
    "easy/Clamp.java",
    "easy/ConvertTemperature.java",
    "easy/IsCommonFactor.java",
    "easy/IsCommonMultiple.java",
    "easy/LeapYear.java",
    "easy/SumSaturated.java",  # was SafeSum.java
    "easy/Swap1.java",
    "easy/Swap2.java",
    "medium/Add.java",
    "medium/AllDigits.java",
    "medium/ArrayAppend.java",
    "medium/CompareArray.java",
    "medium/CopyArray.java",
    "medium/DivArrayByTwo.java",
    "medium/DoubleArrayElements.java",
    "medium/Find.java",
    "medium/IsPalindrome.java",
    "medium/IsPrefix.java",
    "medium/IsReverseArray.java",
    "medium/IsStrictlyDecreasing.java",
    "medium/IsStrictlyMonotonic.java",
    "medium/Max.java",
    "medium/Min.java",
    "medium/ReverseArray.java",
    "hard/Mul.java",
    "hard/TwoSum.java",
}


def get_preliminary_classnames() -> set:
    """Extract classnames from PRELIMINARY_DATASET paths."""
    classnames = set()
    for path in PRELIMINARY_DATASET:
        # Extract classname from path like "easy/Abs1.java" -> "Abs1"
        filename = os.path.basename(path)
        classname = os.path.splitext(filename)[0]
        classnames.add(classname)
    return classnames


def filter_preliminary_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter dataframe to only include rows where 'classname' is in the PRELIMINARY_DATASET.
    """
    if 'classname' not in df.columns:
        raise KeyError("DataFrame must have a 'classname' column to filter by preliminary dataset")

    preliminary_classnames = get_preliminary_classnames()
    return df[df['classname'].isin(preliminary_classnames)].reset_index(drop=True)

def _sorted_results_dirs(all_results_dir: str) -> List[str]:
    """Return absolute paths of results_E* directories under all_results_dir."""
    if not os.path.isdir(all_results_dir):
        raise FileNotFoundError(f"Not a directory: {all_results_dir}")

    entries: List[str] = []
    for name in os.listdir(all_results_dir):
        full = os.path.join(all_results_dir, name)
        if os.path.isdir(full) and name.startswith('results_E'):
            entries.append(full)

    # If the user passes a single results_E* dir as all_results_dir, accept it too.
    base = os.path.basename(os.path.abspath(all_results_dir))
    if os.path.isdir(all_results_dir) and base.startswith('results_E'):
        csv_path = os.path.join(all_results_dir, 'experiments_results.csv')
        if os.path.isfile(csv_path) and all_results_dir not in entries:
            entries.append(all_results_dir)

    def key(path: str):
        name = os.path.basename(path)
        m = re.match(r"^results_E(\d+)$", name)
        return (0, int(m.group(1))) if m else (1, name)

    return sorted(entries, key=key)


def _ensure_columns(df: pd.DataFrame, required_cols: List[str]) -> pd.DataFrame:
    """Ensure all required columns exist; missing ones become NA."""
    out = df.copy()
    for col in required_cols:
        if col not in out.columns:
            out[col] = pd.NA
    return out


def _append_csv(df: pd.DataFrame, path: str, header_cols: List[str], *, append: bool) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    # Default behavior is to overwrite on first write of this run, unless append=True.
    write_header = True
    mode = 'w'
    if append and os.path.exists(path):
        write_header = False
        mode = 'a'

    df.to_csv(path, sep=',', index=False, columns=header_cols, mode=mode, header=write_header)

def avg_mutation_iterations_on_suc(df):
    """
    For each non-incorrect category ('correct_not_complete', 'complete_not_gt', 'complete_gt'),
    compute the average of 'number_of_mut_iterations'.
    Returns a dict like {'correct_not_complete': mean, 'complete_not_gt': mean, 'complete_gt': mean}.
    """
    required = {'result', 'number_of_mut_iterations'}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    tmp = df.copy()
    tmp['result'] = tmp['result'].astype(str).str.strip()
    tmp['number_of_mut_iterations'] = pd.to_numeric(
        tmp['number_of_mut_iterations'], errors='coerce'
    )

    categories = ['correct_not_complete', 'complete_not_gt', 'complete_gt']
    means = (
        tmp[tmp['result'].isin(categories)]
        .groupby('result')['number_of_mut_iterations']
        .mean()
        .reindex(categories)
    )
    return means.to_dict()

def group_results_categories(df):
    """
    Group by experiment and difficulty and count occurrences of result categories.
    Returns dataframe with columns:
            ['experiment','difficulty','count_incorrect','count_correct_not_complete','count_complete_not_gt','count_complete_gt']
    """
    import pandas as pd

    df = df.copy()
    df['result'] = df['result'].astype(str).str.strip()

    counts = (
        df.groupby(['experiment', 'difficulty'])['result']
          .value_counts()
          .unstack(fill_value=0)
    )

    # remove the columns' name so "result" doesn't appear above headers
    counts.columns.name = None

    expected = ['incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']
    for col in expected:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[expected]

    out = counts.reset_index().rename(columns={
        'incorrect': 'count_incorrect',
        'correct_not_complete': 'count_correct_not_complete',
        'complete_not_gt': 'count_complete_not_gt',
        'complete_gt': 'count_complete_gt'
    })

    for c in ['count_incorrect', 'count_correct_not_complete', 'count_complete_not_gt', 'count_complete_gt']:
        out[c] = out[c].astype(int)

    def exp_key(x):
        try:
            return int(x.replace('exp', ''))
        except Exception:
            return x
    diff_order = {'easy': 0, 'medium': 1, 'hard': 2}
    out['_exp_order'] = out['experiment'].apply(exp_key)
    out['_diff_order'] = out['difficulty'].map(diff_order).fillna(99)
    out = (out.sort_values(['_exp_order', '_diff_order'])
              .drop(columns=['_exp_order', '_diff_order'])
              .reset_index(drop=True))

    # also clear any columns name just in case
    out.columns.name = None
    out.index.name = None
    return out

def group_by_classname(df):
    """
    For each (experiment, difficulty, classname), count occurrences of result categories across runs.
    Returns columns:
            ['experiment','difficulty','classname','num_incorrect','num_correct_not_complete','num_complete_not_gt','num_complete_gt']
    """
    required = {'experiment', 'difficulty', 'classname', 'result'}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    tmp = df.copy()
    tmp['result'] = tmp['result'].astype(str).str.strip()
    tmp['difficulty'] = tmp['difficulty'].astype(str).str.strip()

    categories = ['incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']
    counts = (
        tmp.groupby(['experiment', 'difficulty', 'classname'])['result']
           .value_counts()
           .unstack(fill_value=0)
    )

    # Ensure all expected columns exist
    for col in categories:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[categories]

    out = counts.reset_index().rename(columns={
        'incorrect': 'num_incorrect',
        'correct_not_complete': 'num_correct_not_complete',
        'complete_not_gt': 'num_complete_not_gt',
        'complete_gt': 'num_complete_gt'
    })

    # Cast to int and clear index/column names
    for c in ['num_incorrect', 'num_correct_not_complete', 'num_complete_not_gt', 'num_complete_gt']:
        out[c] = out[c].astype(int)
    out.columns.name = None
    out.index.name = None

    # Sort by difficulty: easy, mediun, hard (accept both 'mediun' and 'medium')
    diff_order = {'easy': 0, 'mediun': 1, 'medium': 1, 'hard': 2}
    out['_diff_order'] = out['difficulty'].map(diff_order).fillna(99).astype(int)
    out = (out.sort_values(['_diff_order'])
              .drop(columns=['_diff_order'])
              .reset_index(drop=True))

    return out

def group_impacted_by_mutation(df):
    """
    Creates a table with columns 'experiments', 'difficulty', 'nums_incorrect_with_mutation', 'nums_correct_not_complete_with_mutation', 'nums_complete_not_gt_with_mutation', 'nums_complete_gt_with_mutation'.
    This function sees the entries that have int('number_of_mut_iterations') > 0 and groups by the result and difficulty
    """
    required = {'experiment', 'difficulty', 'result', 'number_of_mut_iterations'}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    tmp = df.copy()
    tmp['result'] = tmp['result'].astype(str).str.strip()
    tmp['difficulty'] = tmp['difficulty'].astype(str).str.strip()
    tmp['experiment'] = tmp['experiment'].astype(str).str.strip()
    tmp['number_of_mut_iterations'] = pd.to_numeric(
        tmp['number_of_mut_iterations'], errors='coerce'
    ).fillna(0)

    # Keep all experiment/difficulty pairs present in the input
    pairs = tmp[['experiment', 'difficulty']].drop_duplicates()

    # Filter to rows where mutations happened and results are successful
    categories = ['incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']
    filt = (tmp['number_of_mut_iterations'] > 0) & (tmp['result'].isin(categories))
    tmp = tmp.loc[filt]

    counts = (
        tmp.groupby(['experiment', 'difficulty'])['result']
           .value_counts()
           .unstack(fill_value=0)
    )

    # Ensure all expected success columns exist
    for col in categories:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[categories]

    # Reindex to include all exp/difficulty pairs, filling with zeros
    counts = counts.reindex(
        pd.MultiIndex.from_frame(pairs[['experiment', 'difficulty']]),
        fill_value=0
    )

    out = counts.reset_index().rename(columns={
        'incorrect': 'nums_incorrect_with_mutation',
        'correct_not_complete': 'nums_correct_not_complete_with_mutation',
        'complete_not_gt': 'nums_complete_not_gt_with_mutation',
        'complete_gt': 'nums_complete_gt_with_mutation'
    })

    # Cast counts to int
    for c in ['nums_incorrect_with_mutation', 'nums_correct_not_complete_with_mutation', 'nums_complete_not_gt_with_mutation', 'nums_complete_gt_with_mutation']:
        out[c] = out[c].astype(int)

    # Sort only by difficulty (keep experiment column but don't sort by it)
    diff_order = {'easy': 0, 'mediun': 1, 'medium': 1, 'hard': 2}
    out['_diff_order'] = out['difficulty'].map(diff_order).fillna(99).astype(int)
    out = out.sort_values(['_diff_order']).drop(columns=['_diff_order']).reset_index(drop=True)

    # Place experiment column at the end
    desired_cols = [
        'experiment',
        'difficulty',
        'nums_incorrect_with_mutation',
        'nums_correct_not_complete_with_mutation',
        'nums_complete_not_gt_with_mutation',
        'nums_complete_gt_with_mutation',
    ]
    out = out[desired_cols]

    out.columns.name = None
    out.index.name = None
    return out

def see_impact_of_embedded_compl(df):
    """
    This looks at how many 'correct_not_complete', 'complete_not_gt' and 'complete_gt' results had the 'had_embedded_compl_check' True
    Outputs a table with columns 'experiment', 'difficulty', 'num_correct_not_complete_with_embedded_compl', 'num_complete_not_gt_with_embedded_compl' and 'num_complete_gt_with_embedded_compl'
    """
    required = {'experiment', 'difficulty', 'result', 'had_embedded_compl_check'}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    tmp = df.copy()
    tmp['experiment'] = tmp['experiment'].astype(str).str.strip()
    tmp['difficulty'] = tmp['difficulty'].astype(str).str.strip()
    tmp['result'] = tmp['result'].astype(str).str.strip()

    # Normalize to boolean
    if tmp['had_embedded_compl_check'].dtype != bool:
        mapped = (
            tmp['had_embedded_compl_check']
            .astype(str)
            .str.strip()
            .str.lower()
            .map({
                'true': True, 't': True, '1': True, 'yes': True, 'y': True,
                'false': False, 'f': False, '0': False, 'no': False, 'n': False, '': False
            })
        )
        tmp['had_embedded_compl_check'] = mapped.fillna(False).astype(bool)

    # Keep all experiment/difficulty pairs
    pairs = tmp[['experiment', 'difficulty']].drop_duplicates()

    # Filter to successes that had embedded completeness check
    categories = ['correct_not_complete', 'complete_not_gt', 'complete_gt']
    tmp = tmp[(tmp['result'].isin(categories)) & (tmp['had_embedded_compl_check'])]

    counts = (
        tmp.groupby(['experiment', 'difficulty'])['result']
           .value_counts()
           .unstack(fill_value=0)
    )

    # Ensure expected columns
    for col in categories:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[categories]

    # Include missing exp/difficulty pairs with zeros
    counts = counts.reindex(
        pd.MultiIndex.from_frame(pairs[['experiment', 'difficulty']]),
        fill_value=0
    )

    out = counts.reset_index().rename(columns={
        'correct_not_complete': 'num_correct_not_complete_with_embedded_compl',
        'complete_not_gt': 'num_complete_not_gt_with_embedded_compl',
        'complete_gt': 'num_complete_gt_with_embedded_compl'
    })

    # Cast to int
    for c in ['num_correct_not_complete_with_embedded_compl', 'num_complete_not_gt_with_embedded_compl', 'num_complete_gt_with_embedded_compl']:
        out[c] = out[c].astype(int)

    # Sort only by difficulty
    diff_order = {'easy': 0, 'mediun': 1, 'medium': 1, 'hard': 2}
    out['_diff_order'] = out['difficulty'].map(diff_order).fillna(99).astype(int)
    out = out.sort_values(['_diff_order']).drop(columns=['_diff_order']).reset_index(drop=True)

    # Keep experiment column at the end
    out = out[
        ['experiment',
         'difficulty',
            'num_correct_not_complete_with_embedded_compl',
            'num_complete_not_gt_with_embedded_compl',
         'num_complete_gt_with_embedded_compl']
    ]

    out.columns.name = None
    out.index.name = None
    return out

def overall_time_avg(df):
    """
    Compute the average time per experiment.
    Returns a DataFrame with columns ['experiment', 'time_avg'].
    """
    required = {'experiment', 'time'}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    tmp = df.copy()
    tmp['time'] = pd.to_numeric(tmp['time'], errors='coerce')

    out = tmp.groupby('experiment', sort=False)['time'].mean().reset_index()
    out.columns = ['experiment', 'time_avg']

    def exp_key(x):
        try:
            return int(x.replace('exp', ''))
        except Exception:
            return x
    out['_order'] = out['experiment'].apply(exp_key)
    out = out.sort_values('_order').drop(columns=['_order']).reset_index(drop=True)

    out.columns.name = None
    out.index.name = None
    return out


def avg_time_per_difficulty(df):
    """
    Compute the average time per experiment and difficulty.
    Returns a DataFrame with columns ['experiment', 'difficulty', 'time_avg'].
    """
    required = {'experiment', 'difficulty', 'time'}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    tmp = df.copy()
    tmp['time'] = pd.to_numeric(tmp['time'], errors='coerce')
    tmp['difficulty'] = tmp['difficulty'].astype(str).str.strip()

    out = tmp.groupby(['experiment', 'difficulty'], sort=False)['time'].mean().reset_index()
    out.columns = ['experiment', 'difficulty', 'time_avg']

    def exp_key(x):
        try:
            return int(x.replace('exp', ''))
        except Exception:
            return x
    diff_order = {'easy': 0, 'medium': 1, 'hard': 2}
    out['_exp_order'] = out['experiment'].apply(exp_key)
    out['_diff_order'] = out['difficulty'].map(diff_order).fillna(99)
    out = (out.sort_values(['_exp_order', '_diff_order'])
              .drop(columns=['_exp_order', '_diff_order'])
              .reset_index(drop=True))

    out.columns.name = None
    out.index.name = None
    return out


def number_of_times_llm_gave_up(df):
    """
    For each 'result': incorrect, correct_not_complete, complete_not_gt, complete_gt, grouped by difficulty: 'easy', 'medium', 'hard'
    Get if the number of times the LLM gave up, by the column 'llm_gave_up', which has values True or False
    Outputs a table containing 'experiment','difficulty','gave_up_incorrect','gave_up_correct_not_complete','gave_up_complete_not_gt','gave_up_complete_gt'
    """
    required = {'experiment', 'difficulty', 'result', 'llm_gave_up'}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    tmp = df.copy()
    tmp['experiment'] = tmp['experiment'].astype(str).str.strip()
    tmp['difficulty'] = tmp['difficulty'].astype(str).str.strip()
    tmp['result'] = tmp['result'].astype(str).str.strip()

    # Normalize llm_gave_up to boolean
    if tmp['llm_gave_up'].dtype != bool:
        mapped = (
            tmp['llm_gave_up']
            .astype(str)
            .str.strip()
            .str.lower()
            .map({
                'true': True, 't': True, '1': True, 'yes': True, 'y': True,
                'false': False, 'f': False, '0': False, 'no': False, 'n': False, '': False
            })
        )
        tmp['llm_gave_up'] = mapped.fillna(False).astype(bool)

    # Keep all experiment/difficulty pairs to reindex later
    pairs = tmp[['experiment', 'difficulty']].drop_duplicates()

    # Filter only rows where the LLM gave up
    tmp = tmp[tmp['llm_gave_up']]

    categories = ['incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']
    counts = (
        tmp.groupby(['experiment', 'difficulty'])['result']
           .value_counts()
           .unstack(fill_value=0)
    )

    # Ensure all expected category columns exist
    for col in categories:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[categories]

    # Reindex to include all exp/difficulty pairs, fill with zeros
    counts = counts.reindex(
        pd.MultiIndex.from_frame(pairs[['experiment', 'difficulty']]),
        fill_value=0
    )

    out = counts.reset_index().rename(columns={
        'incorrect': 'gave_up_incorrect',
        'correct_not_complete': 'gave_up_correct_not_complete',
        'complete_not_gt': 'gave_up_complete_not_gt',
        'complete_gt': 'gave_up_complete_gt'
    })

    # Cast to int
    for c in ['gave_up_incorrect', 'gave_up_correct_not_complete', 'gave_up_complete_not_gt', 'gave_up_complete_gt']:
        out[c] = out[c].astype(int)

    # Sort only by difficulty
    diff_order = {'easy': 0, 'medium': 1, 'hard': 2}
    out['_diff_order'] = out['difficulty'].map(diff_order).fillna(99).astype(int)
    out = out.sort_values(['_diff_order']).drop(columns=['_diff_order']).reset_index(drop=True)

    # Keep experiment column first
    out = out[
        ['experiment', 'difficulty', 'gave_up_incorrect', 'gave_up_correct_not_complete', 'gave_up_complete_not_gt', 'gave_up_complete_gt']
    ]

    out.columns.name = None
    out.index.name = None
    return out



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=(
            "Process an all_results directory containing multiple results_E* directories. "
            "For each results_E* directory, read experiments_results.csv, print the same stdout tables, "
            "and also write combined CSV outputs."
        )
    )
    parser.add_argument(
        "all_results",
        help=(
            "Directory containing results_E* directories (or a single results_E* directory). "
            "Each results_E* must contain experiments_results.csv"
        ),
    )
    parser.add_argument(
        "--combined_csv",
        default=None,
        help="Output path for combined_results.csv (default: <all_results>/combined_results.csv)",
    )
    parser.add_argument(
        "--grouped_csv",
        default=None,
        help=(
            "Output path for grouped_data_classification_only.csv "
            "(default: <all_results>/grouped_data_classification_only.csv)"
        ),
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to output CSVs if they already exist (otherwise overwrite).",
    )
    parser.add_argument(
        "--preliminary",
        action="store_true",
        default=False,
        help="Filter results to only include samples from the PRELIMINARY_DATASET (32 samples).",
    )
    parser.add_argument(
        "--overall_csv",
        default=None,
        help="Output path for overall_results.csv (default: <all_results>/overall_results.csv)",
    )
    parser.add_argument(
        "--mutation_csv",
        default=None,
        help="Output path for mutation.csv (default: <all_results>/mutation.csv)",
    )
    parser.add_argument(
        "--completeness_csv",
        default=None,
        help="Output path for completeness.csv (default: <all_results>/completeness.csv)",
    )
    parser.add_argument(
        "--overall_time_avg_csv",
        default=None,
        help="Output path for overall_time_avg.csv (default: <all_results>/overall_time_avg.csv)",
    )
    parser.add_argument(
        "--time_avg_per_difficulty_csv",
        default=None,
        help="Output path for time_avg_per_difficulty.csv (default: <all_results>/time_avg_per_difficulty.csv)",
    )
    args = parser.parse_args()

    combined_csv = args.combined_csv or os.path.join(args.all_results, 'combined_results.csv')
    grouped_csv = args.grouped_csv or os.path.join(args.all_results, 'grouped_data_classification_only.csv')
    overall_csv = args.overall_csv or os.path.join(args.all_results, 'overall_results.csv')
    mutation_csv = args.mutation_csv or os.path.join(args.all_results, 'mutation.csv')
    completeness_csv = args.completeness_csv or os.path.join(args.all_results, 'completeness.csv')
    overall_time_avg_csv = args.overall_time_avg_csv or os.path.join(args.all_results, 'overall_time_avg.csv')
    time_avg_per_difficulty_csv = args.time_avg_per_difficulty_csv or os.path.join(args.all_results, 'time_avg_per_difficulty.csv')

    # If not appending, clear outputs once per run.
    if not args.append:
        for p in [combined_csv, grouped_csv, overall_csv, mutation_csv, completeness_csv, overall_time_avg_csv, time_avg_per_difficulty_csv]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

    results_dirs = _sorted_results_dirs(args.all_results)
    if not results_dirs:
        raise FileNotFoundError(
            f"No results_E* directories found under: {args.all_results}"
        )

    for results_dir in results_dirs:
        results_csv_path = os.path.join(results_dir, 'experiments_results.csv')
        if not os.path.isfile(results_csv_path):
            continue

        df = pd.read_csv(results_csv_path)

        # Extract experiment name from directory (e.g., "results_E1")
        exp_name = os.path.basename(os.path.normpath(results_dir))

        # Filter to preliminary dataset if requested
        if args.preliminary:
            df = filter_preliminary_dataset(df)
            print(f"[{exp_name}] Filtered to preliminary dataset: {len(df)} rows")

        # Keep stdout printing behavior (same tables as before) for each directory.
        categories = ['incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']
        counts = df['result'].value_counts().reindex(categories, fill_value=0)

        # Write overall results to CSV
        overall_row = pd.DataFrame([{
            'experiment': exp_name,
            'incorrect': counts.get('incorrect', 0),
            'correct_not_complete': counts.get('correct_not_complete', 0),
            'complete_not_gt': counts.get('complete_not_gt', 0),
            'complete_gt': counts.get('complete_gt', 0),
        }])
        print(f"[{exp_name}] Overall results:")
        print(overall_row.to_csv(sep=',', index=False))
        _append_csv(
            overall_row,
            overall_csv,
            ['experiment', 'incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt'],
            append=True,
        )

        grouped_df = group_results_categories(df)
        print('Grouped by difficulty')
        print(grouped_df.to_csv(sep=',', index=False))

        grouped_impacted_by_mutation = group_impacted_by_mutation(df)
        print('Grouped impacted by mutation')
        print(grouped_impacted_by_mutation.to_csv(sep=',', index=False))
        _append_csv(
            grouped_impacted_by_mutation,
            mutation_csv,
            ['experiment', 'difficulty', 'nums_incorrect_with_mutation', 'nums_correct_not_complete_with_mutation', 'nums_complete_not_gt_with_mutation', 'nums_complete_gt_with_mutation'],
            append=True,
        )

        impacted_by_embedded_compl = see_impact_of_embedded_compl(df)
        print('Impacted by embedded completeness')
        print(impacted_by_embedded_compl.to_csv(sep=',', index=False))
        _append_csv(
            impacted_by_embedded_compl,
            completeness_csv,
            ['experiment', 'difficulty', 'num_correct_not_complete_with_embedded_compl', 'num_complete_not_gt_with_embedded_compl', 'num_complete_gt_with_embedded_compl'],
            append=True,
        )

        # Compute and write overall time average
        time_avg_overall_df = overall_time_avg(df)
        print('Overall time average')
        print(time_avg_overall_df.to_csv(sep=',', index=False))
        _append_csv(
            time_avg_overall_df,
            overall_time_avg_csv,
            ['experiment', 'time_avg'],
            append=True,
        )

        # Compute and write time average per difficulty
        time_avg_diff_df = avg_time_per_difficulty(df)
        print('Average time per difficulty')
        print(time_avg_diff_df.to_csv(sep=',', index=False))
        _append_csv(
            time_avg_diff_df,
            time_avg_per_difficulty_csv,
            ['experiment', 'difficulty', 'time_avg'],
            append=True,
        )

        # Append combined raw rows
        combined_df = _ensure_columns(df, COMBINED_RESULTS_COLUMNS)[COMBINED_RESULTS_COLUMNS]
        _append_csv(combined_df, combined_csv, COMBINED_RESULTS_COLUMNS, append=True)

        # Append grouped classification-only counts
        grouped_for_csv = grouped_df.rename(columns={
            'count_incorrect': 'incorrect',
            'count_correct_not_complete': 'correct_not_complete',
            'count_complete_not_gt': 'complete_not_gt',
            'count_complete_gt': 'complete_gt',
        })
        grouped_for_csv = _ensure_columns(
            grouped_for_csv,
            ['experiment', 'difficulty', 'incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt'],
        )
        grouped_for_csv = grouped_for_csv[
            ['experiment', 'difficulty', 'incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']
        ]
        _append_csv(
            grouped_for_csv,
            grouped_csv,
            ['experiment', 'difficulty', 'incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt'],
            append=True,
        )
