import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
import numpy as np
import seaborn as sns
import matplotlib.colors as mcolors
import argparse
import os
import re

# 0 no change
def lighten_color(color, amount=0.2):
    rgb = np.array(mcolors.to_rgb(color), dtype=float)
    white = np.array([1.0, 1.0, 1.0], dtype=float)
    blended = (1 - amount) * rgb + amount * white
    blended = np.clip(blended, 0.0, 1.0)
    return mcolors.to_hex(tuple(blended))


def _parse_experiment_number(experiment: str):
    """Extract integer experiment number from 'expN' or 'results_EN'. Returns None if unknown."""
    s = str(experiment).strip()
    m = re.match(r'^exp(\d+)$', s)
    if m:
        return int(m.group(1))
    m = re.match(r'^results_E(\d+)$', s)
    if m:
        return int(m.group(1))
    return None


def _validate_consistent_sample_counts(df: pd.DataFrame) -> None:
    """Ensure every experiment has the same number of samples for each difficulty."""
    cats = ['incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']
    if not all(c in df.columns for c in cats):
        return
    tmp = df.copy()
    tmp['_total'] = tmp[cats].sum(axis=1)
    for diff, group in tmp.groupby('difficulty'):
        unique_totals = group['_total'].unique()
        if len(unique_totals) > 1:
            details = dict(zip(group['experiment'], group['_total']))
            raise ValueError(
                f"Inconsistent sample counts for difficulty '{diff}': {details}. "
                f"All experiments must have the same number of samples per difficulty."
            )


def _resolve_input_to_grouped_df(input_path: str) -> pd.DataFrame:
    """Load grouped classification-only results from a CSV or from an all_results directory."""
    if os.path.isfile(input_path):
        result = pd.read_csv(input_path)
        _validate_consistent_sample_counts(result)
        return result

    if not os.path.isdir(input_path):
        raise FileNotFoundError(f"Input path not found: {input_path}")

    grouped_candidate = os.path.join(input_path, 'grouped_data_classification_only.csv')
    if os.path.isfile(grouped_candidate):
        result = pd.read_csv(grouped_candidate)
        _validate_consistent_sample_counts(result)
        return result

    # Otherwise, attempt to build from results_E*/experiments_results.csv.
    rows = []
    for name in os.listdir(input_path):
        d = os.path.join(input_path, name)
        if not (os.path.isdir(d) and name.startswith('results_E')):
            continue
        csv_path = os.path.join(d, 'experiments_results.csv')
        if os.path.isfile(csv_path):
            rows.append(pd.read_csv(csv_path))

    if not rows:
        raise FileNotFoundError(
            f"No grouped_data_classification_only.csv and no results_E*/experiments_results.csv found under: {input_path}"
        )

    tmp = pd.concat(rows, ignore_index=True)
    required = {'experiment', 'difficulty', 'result'}
    missing = [c for c in required if c not in tmp.columns]
    if missing:
        raise KeyError(f"Missing required columns in experiments_results.csv: {missing}")

    tmp['experiment'] = tmp['experiment'].astype(str).str.strip()
    tmp['difficulty'] = tmp['difficulty'].astype(str).str.strip()
    tmp['result'] = tmp['result'].astype(str).str.strip()

    categories = ['incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']
    counts = (
        tmp.groupby(['experiment', 'difficulty'])['result']
           .value_counts()
           .unstack(fill_value=0)
    )
    for col in categories:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[categories]
    out = counts.reset_index()
    out.columns.name = None
    out.index.name = None
    _validate_consistent_sample_counts(out)
    return out

def create_graphics(experiments, custom_labels=None, *, df: pd.DataFrame | None = None, out_dir: str = 'figures'):
    """
    df is a dataframe containing columns:
    experiment,difficulty,incorrect,correct_not_complete,complete_not_gt,complete_gt
    each 'experiment' has three entries, one for each difficulty: easy,medium,hard
    incorrect,correct_not_complete,complete_not_gt,complete_gt are integers

    Args:
        experiments: list of experiment IDs (e.g., ['exp1', 'exp2', 'exp3'])
        custom_labels: optional list of custom labels for each experiment (same length as experiments)
                      Use None for any experiment to fall back to the default label
    """

    if df is None:
        df = pd.read_csv('exp_results/grouped_data_classification_only.csv')

    # Normalize and ensure numeric columns
    df = df.copy()
    df['experiment'] = df['experiment'].astype(str).str.strip()
    df['difficulty'] = df['difficulty'].astype(str).str.strip()

    for col in ['incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    df['_exp_num'] = df['experiment'].apply(_parse_experiment_number)
    df = df[df['_exp_num'].notna()].copy()
    df['_exp_num'] = df['_exp_num'].astype(int)

    # REMAP DATA SOURCE TO NEW EXPERIMENT NUMBERS
    mapping = {
        1: 1, 2: 2, 3: 3, 4: 4, 
        6: 5, 
        8: 6, 9: 7, 11: 8, 
        13: 9, 14: 10, 16: 11
    }
    df = df[df['_exp_num'].isin(mapping.keys())].copy()
    df['_exp_num'] = df['_exp_num'].map(mapping)

    # Mapping experiment number -> label shown
    experiment_names = {
        1: 'E1: SpecGen\nwith asm',
        2: 'E2: Convers.\nwith asm',
        3: 'E3: SpecGen',
        4: 'E4: Convers.',
        5: 'E5: Convers.\n+ EC',
        6: 'E6: SpecGen',
        7: 'E7: Convers.',
        8: 'E8: Convers.\n+ EC',
        9: 'E9: SpecGen',
        10: 'E10: Convers.',
        11: 'E11: Convers.\n+ EC',
    }

    # Override with custom labels if provided
    if custom_labels is not None:
        if len(custom_labels) != len(experiments):
            raise ValueError(f"custom_labels length ({len(custom_labels)}) must match experiments length ({len(experiments)})")
        for exp, custom_label in zip(experiments, custom_labels):
            exp_num = _parse_experiment_number(exp)
            if exp_num is None:
                continue
            if custom_label is not None:
                experiment_names[int(exp_num)] = custom_label

    exp_nums = []
    for e in experiments:
        n = _parse_experiment_number(e)
        if n is None:
            raise ValueError(f"Unrecognized experiment id: {e} (expected expN or results_EN)")
        exp_nums.append(int(n))

    difficulties = ['easy', 'medium', 'hard']
    categories = ['incorrect', 'correct_not_complete', 'complete_not_gt', 'complete_gt']

    # okabe ito color palette for color blindness
    categories_colors = ["#d55e00", "#f0e442", "#0072b2", "#009e73"]
    categories_colors = [lighten_color(c, 0.3) for c in categories_colors]

    num_samples_by_difficulty = {}
    for diff in difficulties:
        diff_rows = df[df['difficulty'] == diff]
        if not diff_rows.empty:
            totals = diff_rows[categories].sum(axis=1)
            num_samples_by_difficulty[diff] = int(totals.iloc[0])

    # Make a 100% stacked bar chart
    # The stacks must be in the following order (bottom to top):
    # incorrect, correct_not_complete, complete_not_gt, complete_gt

    # Divide in three sections, one for each difficulty, in the following order: easy, medium, hard
    # Each section must contain the respective entry for each experiment

    # Do not add one label per chart. Instead, make a single label at the bottom,
    # containing the color-category label.

    # In the middle of each stack, add a label with the percentage, with 1 decimal place.
    # Show every percentage, except the ones below the threshold:
    PERCENTAGE_LABEL_THRESHHOLD=5.0

    # Outside-percentage annotation controls (for values below threshold)
    OUTSIDE_LABEL_OFFSET_POINTS = 5   # horizontal gap from bar edge (in points)
    OUTSIDE_LABEL_FONT_SIZE = 10 if len(exp_nums) >= 3 else 12
    OUTSIDE_LABEL_FONT_WEIGHT = 'bold'
    OUTSIDE_ARROW_STYLE = '-'
    OUTSIDE_ARROW_COLOR = '#444444'
    OUTSIDE_ARROW_LINEWIDTH = 2
    OUTSIDE_LABEL_SIDE = 'right'   # 'right' or 'left'
    OUTSIDE_LABEL_Y_OFFSET_POINTS = 12  # vertical offset (points) for outside labels; alternates -Y,0,Y this value

    # Make bars thicker (0<width<=1; 1 means bars touch)
    BAR_WIDTH = 0.93

    # Legend spacing controls (increase these to add more gap)
    LEGEND_Y_OFFSET = -0.13        # more negative -> legend lower
    LEGEND_BORDERAXESPAD = 0.8    # bigger -> more gap between axes and legend
    BOTTOM_MARGIN = 0.25          # bigger -> more space reserved at bottom

    # Option: incline experiment labels (slanted x-ticks)
    ROTATE_XTICK_LABELS = True
    XTICK_LABEL_ROTATION = 30      # degrees (e.g., 30, 45)
    XTICK_LABEL_HALIGN = 'right'   # 'right' works well with positive rotation

    # Do not add a top figure title. In each section, add the difficulty in the top

    # Aesthetics
    sns.set_theme(style='whitegrid')
    plt.rcParams.update({
        'axes.edgecolor': '#999999',
        'axes.linewidth': 0.6,
        'grid.color': '#DDDDDD',
        'grid.linestyle': '-',
        'grid.linewidth': 0.6,
    })

    # Pretty legend labels
    legend_labels = {
        'incorrect': 'Incorrect',
        'correct_not_complete': 'Correct',
        'complete_not_gt': 'Complete\nnot GT',
        'complete_gt': 'Complete GT',
    }

    # Create subplots: one column per difficulty
    n_sections = len(difficulties)
    fig, axes = plt.subplots(1, n_sections, figsize=(7.16, 5.0), sharey=True)

    if n_sections == 1:
        axes = [axes]

    # Plot each difficulty section
    for ax, diff in zip(axes, difficulties):
        # Filter and order by experiment
        sub = (
            df[df['difficulty'] == diff]
            .set_index('_exp_num')
            .reindex(list(exp_nums))
            .reset_index()
        )

        # Guard against missing experiments
        if sub.empty:
            ax.set_axis_off()
            continue

        # Compute percentages row-wise (100% stacked)
        totals = sub[categories].sum(axis=1)
        totals = totals.replace(0, np.nan)  # avoid division by zero
        percs = sub[categories].div(totals, axis=0).fillna(0) * 100.0

        x = np.arange(len(sub))
        width = BAR_WIDTH

        # Cumulative bottom for stacking
        bottoms = np.zeros(len(sub))
        # Alternate vertical offset for each outside arrow per bar
        arrow_index = [0] * len(sub)

        # Pre-count outside labels per bar to decide whether to alternate Y offset
        outside_count_per_bar = [0] * len(sub)
        for cat in categories:
            for bar_i, h in enumerate(percs[cat].to_numpy()):
                if 0 < h < PERCENTAGE_LABEL_THRESHHOLD:
                    outside_count_per_bar[bar_i] += 1

        # Stacked bars in required order incorrect,correct_not_complete,complete_not_gt,complete_gt
        for cat, color in zip(categories, categories_colors):
            heights = percs[cat].to_numpy()
            bars = ax.bar(
                x, heights, bottom=bottoms, width=width,
                color=color, edgecolor='white', linewidth=0.4
            )

            # Percentage labels: inside if >= threshold, otherwise outside with arrow
            for bar_i, (rect, h, b) in enumerate(zip(bars, heights, bottoms)):
                if h >= PERCENTAGE_LABEL_THRESHHOLD:
                    ax.text(
                        rect.get_x() + rect.get_width() / 2.0,
                        b + h / 2.0,
                        f"{h:.1f}%",
                        ha='center', va='center',
                        fontsize=10 if len(exp_nums) >= 3 else 13, fontweight='bold', color='black',
                        clip_on=True
                    )
                elif 0 < h < PERCENTAGE_LABEL_THRESHHOLD:
                    # Place annotation to the chosen side with an arrow
                    y_mid = b + h / 2.0
                    if OUTSIDE_LABEL_SIDE == 'left':
                        x_edge = rect.get_x()
                        x_off = -OUTSIDE_LABEL_OFFSET_POINTS
                        ha = 'right'
                    else:
                        x_edge = rect.get_x() + rect.get_width()
                        x_off = OUTSIDE_LABEL_OFFSET_POINTS
                        ha = 'left'
                    # Alternate Y offset only if this bar has more than one outside label
                    if outside_count_per_bar[bar_i] > 1:
                        y_sign = -1 if (arrow_index[bar_i] % 3 == 0) else 0 if (arrow_index[bar_i] % 3 == 1) else 1
                    else:
                        y_sign = 0
                    y_off = y_sign * OUTSIDE_LABEL_Y_OFFSET_POINTS
                    ann = ax.annotate(
                        f"{h:.1f}%",
                        xy=(x_edge, y_mid),                 # arrow tip at bar edge
                        xytext=(x_off, y_off),
                        textcoords='offset points',
                        ha=ha, va='center',
                        fontsize=OUTSIDE_LABEL_FONT_SIZE,
                        fontweight=OUTSIDE_LABEL_FONT_WEIGHT,
                        color='black',
                        arrowprops=dict(
                            arrowstyle=OUTSIDE_ARROW_STYLE,
                            color=OUTSIDE_ARROW_COLOR,
                            lw=OUTSIDE_ARROW_LINEWIDTH
                        ),
                        annotation_clip=False,
                        zorder=5
                    )

                    # Add light stroke for readability over grid
                    ann.set_path_effects([pe.withStroke(linewidth=2, foreground='white')])
                    arrow_index[bar_i] += 1
            bottoms += heights

        # X ticks as experiment short names
        ax.set_xticks(x, [experiment_names.get(int(e), f"E{int(e)}") for e in sub['_exp_num']])

        if ROTATE_XTICK_LABELS:
            # Slant labels to improve readability for long names
            plt.setp(ax.get_xticklabels(),
                     rotation=XTICK_LABEL_ROTATION,
                     ha=XTICK_LABEL_HALIGN,
                     rotation_mode='anchor')
        # Font size for experiment names
        ax.tick_params(axis='x', labelsize=14, pad=6)
        # Font size for Y axis ticks
        ax.tick_params(axis='y', labelsize=14)

        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.tick_params(axis='y', labelsize=14)
        ax.set_yticklabels([f"{v}" for v in [0, 25, 50, 75, 100]])
        #ax.set_xlabel('Experiment')
        # Trim side padding so thicker bars don't look cramped
        ax.margins(x=0.08)
        ax.grid(axis='y', linestyle='-', alpha=0.6)

        # Section title (difficulty at the top)
        n = num_samples_by_difficulty.get(diff)
        title = f"{diff.capitalize()} (n={n//10}x10)" if n is not None else diff.capitalize()
        ax.set_title(title, pad=24, fontsize=13, fontweight='bold')

        # Clean look
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)

    axes[0].set_ylabel('% of samples with result', fontsize=15)

    # Single legend at bottom
    handles = [Patch(facecolor=c, edgecolor='white', label=legend_labels[k])
               for k, c in zip(categories, categories_colors)]
    fig.legend(
        handles=handles,
        loc='lower center',
        ncol=len(categories),
        frameon=False,
        bbox_to_anchor=(0.5, LEGEND_Y_OFFSET),
        borderaxespad=LEGEND_BORDERAXESPAD,
        columnspacing=0.6,    # gap between legend entries (handles) horizontally
        handlelength=1.2,     # shorter patch/handle so entries sit closer
        labelspacing=0.4,     # vertical spacing (only matters if multiple rows)
        fontsize=15           # category labels font size
    )

    plt.subplots_adjust(bottom=BOTTOM_MARGIN, wspace=0.15)
    #plt.tight_layout()

    fig_name = f"{'_'.join(str(n) for n in exp_nums)}.pdf"

    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(os.path.join(out_dir, fig_name), dpi=600, bbox_inches='tight', format='pdf')
    plt.close()
    #plt.show()

if __name__ == '__main__':
    #1. reproducibility:             {1,2}
    #2. no arith null:               {1,3} {2,4}
    #3. SpecGen vs Conversational:   {3,4} {6,7} {9,10}
    #4. impact of the embedded compl {4,5} {7,8} {10,11}
    #5. changed accross models       {3,6,9} {4,7,10} {5,8,11}

    # Format: each item can be either:
    #   - a list of experiment IDs (uses default labels)
    #   - a tuple of (experiment_list, custom_labels_list)
    all_experiments_comparisons = [
        # reproducibility
        ['exp1', 'exp2'],

        #arith non vs no arith null
        ['exp1', 'exp3'],
        ['exp2', 'exp4'],

        # SpecGen vs Conversational
        ['exp3', 'exp4'],
        ['exp6', 'exp7'],
        ['exp9', 'exp10'],

        #3. impact of the embedded completeness
        ['exp4', 'exp5'],
        ['exp7', 'exp8'],
        ['exp10', 'exp11'],

        # 4. changed accross models
        #(['exp3', 'exp6', 'exp9'], ['E3: GPT-3.5 turbo', 'E6: GPT-4.1 mini', 'E9: GPT-5 mini']),
        #(['exp4', 'exp7', 'exp10'], ['E4: GPT-3.5 turbo', 'E7: GPT-4.1 mini', 'E10: GPT-5 mini']),
        #(['exp5', 'exp8', 'exp11'], ['E5: GPT-3.5 turbo', 'E8: GPT-4.1 mini', 'E11: GPT-5 mini'])
    ]

    parser = argparse.ArgumentParser(
        description=(
            "Generate 100% stacked bar charts for predefined experiment comparisons. "
            "Works with partial/intermediate experiment sets and supports expN or results_EN." 
        )
    )
    parser.add_argument(
        'input',
        nargs='?',
        default='all_results/grouped_data_classification_only.csv',
        help=(
            "Path to grouped_data_classification_only.csv OR an all_results directory containing results_E* directories. "
            "Default: all_results/grouped_data_classification_only.csv"
        ),
    )
    parser.add_argument(
        '--out_dir',
        default='figures',
        help="Output directory for PDFs (default: figures)",
    )
    args = parser.parse_args()

    df = _resolve_input_to_grouped_df(args.input)
    df['experiment'] = df['experiment'].astype(str).str.strip()
    df['_exp_num'] = df['experiment'].apply(_parse_experiment_number)
    df = df[df['_exp_num'].notna()].copy()
    df['_exp_num'] = df['_exp_num'].astype(int)

    mapping = {
        1: 1, 2: 2, 3: 3, 4: 4, 
        6: 5, 
        8: 6, 9: 7, 11: 8, 
        13: 9, 14: 10, 16: 11
    }
    df = df[df['_exp_num'].isin(mapping.keys())].copy()
    df['_exp_num'] = df['_exp_num'].map(mapping)

    exp_nums_available = set(df['_exp_num'].unique().tolist())

    generated = 0
    skipped = 0

    for item in all_experiments_comparisons:
        if isinstance(item, tuple) and len(item) == 2:
            exp_list, custom_labels = item
        else:
            exp_list, custom_labels = item, None

        required_nums = []
        unknown = []
        for e in exp_list:
            n = _parse_experiment_number(e)
            if n is None:
                unknown.append(str(e))
            else:
                required_nums.append(int(n))

        if unknown:
            skipped += 1
            print(f"WARNING: skipping comparison {exp_list} (unknown experiment ids: {unknown})")
            continue

        missing = [n for n in required_nums if n not in exp_nums_available]
        if missing:
            skipped += 1
            print(f"WARNING: skipping comparison {exp_list} (missing experiments: {missing})")
            continue

        # Generate the figure
        create_graphics(exp_list, custom_labels, df=df, out_dir=args.out_dir)
        generated += 1

    print(f"Generated {generated} figures; skipped {skipped} comparisons due to missing data.")
