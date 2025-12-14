import pandas as pd
import argparse
import os

def avg_mutation_iterations_on_suc(df):
    """
    For each success category ('valid', 'complete', 'complete_gt'),
    compute the average of 'number_of_mut_iterations'.
    Returns a dict like {'valid': mean, 'complete': mean, 'complete_gt': mean}.
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

    categories = ['valid', 'complete', 'complete_gt']
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
      ['experiment','difficulty','count_failures','count_valid','count_complete','count_complete_gt']
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

    expected = ['failure', 'valid', 'complete', 'complete_gt']
    for col in expected:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[expected]

    out = counts.reset_index().rename(columns={
        'failure': 'count_failures',
        'valid': 'count_valid',
        'complete': 'count_complete',
        'complete_gt': 'count_complete_gt'
    })

    for c in ['count_failures', 'count_valid', 'count_complete', 'count_complete_gt']:
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
      ['experiment','difficulty','classname','num_failures','num_valid','num_complete','num_complete_gt']
    """
    required = {'experiment', 'difficulty', 'classname', 'result'}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    tmp = df.copy()
    tmp['result'] = tmp['result'].astype(str).str.strip()
    tmp['difficulty'] = tmp['difficulty'].astype(str).str.strip()

    categories = ['failure', 'valid', 'complete', 'complete_gt']
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
        'failure': 'num_failures',
        'valid': 'num_valid',
        'complete': 'num_complete',
        'complete_gt': 'num_complete_gt'
    })

    # Cast to int and clear index/column names
    for c in ['num_failures', 'num_valid', 'num_complete', 'num_complete_gt']:
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
    Creates a table with columns 'experiments', 'difficulty', 'nums_failure_with_mutation', 'nums_valid_with_mutation', 'nums_complete_with_mutation', 'nums_complete_gt_with_mutation'.
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
    success_categories = ['failure', 'valid', 'complete', 'complete_gt']
    filt = (tmp['number_of_mut_iterations'] > 0) & (tmp['result'].isin(success_categories))
    tmp = tmp.loc[filt]

    counts = (
        tmp.groupby(['experiment', 'difficulty'])['result']
           .value_counts()
           .unstack(fill_value=0)
    )

    # Ensure all expected success columns exist
    for col in success_categories:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[success_categories]

    # Reindex to include all exp/difficulty pairs, filling with zeros
    counts = counts.reindex(
        pd.MultiIndex.from_frame(pairs[['experiment', 'difficulty']]),
        fill_value=0
    )

    out = counts.reset_index().rename(columns={
        'failure': 'nums_failure_with_mutation',
        'valid': 'nums_valid_with_mutation',
        'complete': 'nums_complete_with_mutation',
        'complete_gt': 'nums_complete_gt_with_mutation'
    })

    # Cast counts to int
    for c in ['nums_failure_with_mutation', 'nums_valid_with_mutation', 'nums_complete_with_mutation', 'nums_complete_gt_with_mutation']:
        out[c] = out[c].astype(int)

    # Sort only by difficulty (keep experiment column but don't sort by it)
    diff_order = {'easy': 0, 'mediun': 1, 'medium': 1, 'hard': 2}
    out['_diff_order'] = out['difficulty'].map(diff_order).fillna(99).astype(int)
    out = out.sort_values(['_diff_order']).drop(columns=['_diff_order']).reset_index(drop=True)

    # Place experiment column at the end
    desired_cols = [
        'experiment',
        'difficulty',
        'nums_failure_with_mutation',
        'nums_valid_with_mutation',
        'nums_complete_with_mutation',
        'nums_complete_gt_with_mutation',
    ]
    out = out[desired_cols]

    out.columns.name = None
    out.index.name = None
    return out

def see_impact_of_embedded_compl(df):
    """
    This looks at how many 'valid', 'complete' and 'complete_gt' results had the 'had_embedded_compl_check' True
    Outputs a table with columns 'experiment', 'difficulty', 'num_valid_with_embedded_compl', 'num_complete_with_embedded_compl' and 'num_complete_gt_with_embedded_compl'
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
    success_categories = ['valid', 'complete', 'complete_gt']
    tmp = tmp[(tmp['result'].isin(success_categories)) & (tmp['had_embedded_compl_check'])]

    counts = (
        tmp.groupby(['experiment', 'difficulty'])['result']
           .value_counts()
           .unstack(fill_value=0)
    )

    # Ensure expected columns
    for col in success_categories:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[success_categories]

    # Include missing exp/difficulty pairs with zeros
    counts = counts.reindex(
        pd.MultiIndex.from_frame(pairs[['experiment', 'difficulty']]),
        fill_value=0
    )

    out = counts.reset_index().rename(columns={
        'valid': 'num_valid_with_embedded_compl',
        'complete': 'num_complete_with_embedded_compl',
        'complete_gt': 'num_complete_gt_with_embedded_compl'
    })

    # Cast to int
    for c in ['num_valid_with_embedded_compl', 'num_complete_with_embedded_compl', 'num_complete_gt_with_embedded_compl']:
        out[c] = out[c].astype(int)

    # Sort only by difficulty
    diff_order = {'easy': 0, 'mediun': 1, 'medium': 1, 'hard': 2}
    out['_diff_order'] = out['difficulty'].map(diff_order).fillna(99).astype(int)
    out = out.sort_values(['_diff_order']).drop(columns=['_diff_order']).reset_index(drop=True)

    # Keep experiment column at the end
    out = out[
        ['experiment',
         'difficulty',
         'num_valid_with_embedded_compl',
         'num_complete_with_embedded_compl',
         'num_complete_gt_with_embedded_compl']
    ]

    out.columns.name = None
    out.index.name = None
    return out

def number_of_times_llm_gave_up(df):
    """
    For each 'result': failure, valid, complete, complete_gt, grouped by difficulty: 'easy', 'medium', 'hard'
    Get if the number of times the LLM gave up, by the column 'llm_gave_up', which has values True or False
    Outputs a table containing 'experiment','difficulty','gave_up_failure','gave_up_valid','gave_up_complete','gave_up_complete_gt'
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

    categories = ['failure', 'valid', 'complete', 'complete_gt']
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
        'failure': 'gave_up_failure',
        'valid': 'gave_up_valid',
        'complete': 'gave_up_complete',
        'complete_gt': 'gave_up_complete_gt'
    })

    # Cast to int
    for c in ['gave_up_failure', 'gave_up_valid', 'gave_up_complete', 'gave_up_complete_gt']:
        out[c] = out[c].astype(int)

    # Sort only by difficulty
    diff_order = {'easy': 0, 'medium': 1, 'hard': 2}
    out['_diff_order'] = out['difficulty'].map(diff_order).fillna(99).astype(int)
    out = out.sort_values(['_diff_order']).drop(columns=['_diff_order']).reset_index(drop=True)

    # Keep experiment column first
    out = out[
        ['experiment', 'difficulty', 'gave_up_failure', 'gave_up_valid', 'gave_up_complete', 'gave_up_complete_gt']
    ]

    out.columns.name = None
    out.index.name = None
    return out



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process results directory to group values analysis.")
    parser.add_argument("results_csv", help="Path to experiments_results.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.results_csv)

    categories = ['failure', 'valid', 'complete', 'complete_gt']
    counts = df['result'].value_counts().reindex(categories, fill_value=0)
    counts_df = counts.rename_axis('result').reset_index(name='count')
    print(counts_df.to_csv(sep=',', index=False))

    grouped_df = group_results_categories(df)
    print('Grouped by difficulty')
    print(grouped_df.to_csv(sep=',', index=False))

    grouped_impacted_by_mutation = group_impacted_by_mutation(df)
    print('Grouped impacted by mutation')
    print(grouped_impacted_by_mutation.to_csv(sep=',', index=False))

    # This is the data for each testcase individually
    # grouped_classname = group_by_classname(df)
    # selected_cols = ['difficulty', 'classname', 'num_failures', 'num_valid', 'num_complete', 'num_complete_gt']
    # print('Grouped results by classname')
    # print(grouped_classname[selected_cols].to_csv(sep=',', index=False))

    impacted_by_embedded_compl = see_impact_of_embedded_compl(df)
    print('Impacted by embedded completeness')
    print(impacted_by_embedded_compl.to_csv(sep=',', index=False))

    # this is also just a curiosity
    #times_llm_gave_up = number_of_times_llm_gave_up(df)
    #print('Number of times it gave up')
    #print(times_llm_gave_up.to_csv(sep=',', index=False))
