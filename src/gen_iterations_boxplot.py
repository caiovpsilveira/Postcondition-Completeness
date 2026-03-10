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


def _experiment_display_label(exp_num: int) -> str:
    starred = {1, 3, 8, 13}
    return f"E{exp_num}{'*' if exp_num in starred else ''}"


def _resolve_input_to_dataframe(input_path: str) -> pd.DataFrame:
    """Load combined results from a CSV or from an all_results directory."""
    if os.path.isfile(input_path):
        return pd.read_csv(input_path)

    if not os.path.isdir(input_path):
        raise FileNotFoundError(f"Input path not found: {input_path}")

    # If directory already has a precomputed combined_results.csv, prefer it.
    combined_candidate = os.path.join(input_path, 'combined_results.csv')
    if os.path.isfile(combined_candidate):
        return pd.read_csv(combined_candidate)

    # Otherwise, try to build a dataframe by concatenating results_E*/experiments_results.csv.
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
            f"No combined_results.csv and no results_E*/experiments_results.csv found under: {input_path}"
        )
    return pd.concat(rows, ignore_index=True)

if __name__ == '__main__':
    """
    df is a dataframe containing columns
    experiment,run,difficulty,classname,result,time,number_of_iterations_before_first_valid,number_of_gen_iterations,number_of_mut_iterations,llm_gave_up,had_embedded_compl_check
    """

    parser = argparse.ArgumentParser(
        description=(
            "Generate gen-iterations boxplots from a combined results CSV or from an all_results directory. "
            "Works with partial/intermediate experiment sets (no need for all 17)."
        )
    )
    parser.add_argument(
        'input',
        nargs='?',
        default='all_results/combined_results.csv',
        help=(
            "Path to combined_results.csv OR an all_results directory containing results_E* directories. "
            "Default: all_results/combined_results.csv"
        ),
    )
    parser.add_argument(
        '--out_dir',
        default='figures',
        help="Output directory for PDFs (default: figures)",
    )
    parser.add_argument(
        '--prefix',
        default='gen_iterations_boxplot',
        help="Output filename prefix (default: gen_iterations_boxplot)",
    )
    args = parser.parse_args()

    df = _resolve_input_to_dataframe(args.input)

    """
    For each difficulty, plot the box plot of the 'number_of_gen_iterations' of each experiment.
    In each experiment x difficulty, you should group the runs by 'result' to create a list with the number of gen_iterations
    for the whole experiment x difficulty

    Then, create a figure for each difficulty.
    Each figure must containt all 17 experiments.
    Each experiment must contain the 4 result categories. If a category does not have any data, it should not be plotted.
    """

    difficulties = ['easy', 'medium', 'hard']
    categories = ['failure', 'valid', 'complete', 'complete_gt']
    category_labels = ['Failure', 'Valid', 'Complete', 'Complete GT']

    # Normalize data
    df['experiment'] = df['experiment'].astype(str).str.strip()
    df['difficulty'] = df['difficulty'].astype(str).str.strip()
    df['result'] = df['result'].astype(str).str.strip()
    df['number_of_gen_iterations'] = pd.to_numeric(df['number_of_gen_iterations'], errors='coerce')

    df['_exp_num'] = df['experiment'].apply(_parse_experiment_number)
    df = df[df['_exp_num'].notna()].copy()
    df['_exp_num'] = df['_exp_num'].astype(int)
    df['_exp_label'] = df['_exp_num'].apply(_experiment_display_label)

    # Infer which experiments exist in the data, ordered by number
    exp_nums_present = sorted(df['_exp_num'].unique().tolist())

    # Filter rows to categories we will plot directly (no renaming)
    plot_df = df[df['result'].isin(categories)]

    # Color palette per category (base + lighter variants for visual separation inside each experiment)
    categories_colors = ["#d55e00", "#f0e442", "#0072b2", "#009e73"]
    categories_colors = [lighten_color(c, -0.30) for c in categories_colors]

    base_colors = {
        'failure': categories_colors[0],
        'valid': categories_colors[1],
        'complete':  categories_colors[2],
        'complete_gt':  categories_colors[3],
    }

    # Create output directory if needed
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    # For spacing: for each experiment we place k boxes with small offsets
    for dif in difficulties:
        dif_df = plot_df[plot_df['difficulty'] == dif]
        if dif_df.empty:
            continue

        # Collect iteration data per experiment/category
        data_entries = []
        for exp_num in exp_nums_present:
            sub = dif_df[dif_df['_exp_num'] == exp_num]
            if sub.empty:
                continue
            exp_label = _experiment_display_label(exp_num)
            for cat in categories:
                subset_cat = sub[sub['result'] == cat]
                if subset_cat.empty:
                    continue
                iterations = subset_cat['number_of_gen_iterations'].tolist()
                data_entries.append((exp_num, exp_label, cat, iterations))

        if not data_entries:
            continue

        # Initialize containers
        positions = []
        box_data = []
        labels = []
        exp_center_positions = {}

        # Layout parameters
        width = 0.1
        inner_gap = 0.025
        gap_between_experiments = 0.6
        cat_order = categories
        cat_index_map = {c: i for i, c in enumerate(cat_order)}

        current_x = 0.0
        last_exp = None
        base_pos_map = {}

        for exp_num, exp_label, cat, iterations in data_entries:
            if exp_num != last_exp:
                if last_exp is not None:
                    current_x += gap_between_experiments
                last_exp = exp_num
                base_pos_map[exp_num] = current_x
            base_x = base_pos_map[exp_num]
            offset = (cat_index_map[cat] - 1.5) * (width + inner_gap)
            pos = base_x + offset
            positions.append(pos)
            box_data.append(iterations)
            labels.append(exp_label)
            exp_center_positions[exp_label] = base_x

        plt.figure(figsize=(7.16, 4.0))
        ax = plt.gca()
        bp = ax.boxplot(
            box_data,
            positions=positions,
            widths=width,
            patch_artist=True,
            manage_ticks=False,
            flierprops=dict(marker='o', markersize=2, markerfacecolor='white', markeredgecolor='#666666', alpha=0.7, linestyle='none')
        )

        # Style boxes
        for i, (_, exp_label, cat, _) in enumerate(data_entries):
            box = bp['boxes'][i]
            color = base_colors[cat]
            box.set_facecolor(lighten_color(color, 0.35))
            box.set_edgecolor(color)
            box.set_linewidth(0.8)
            for w in [bp['whiskers'][2*i], bp['whiskers'][2*i+1]]:
                w.set_color('black'); w.set_linewidth(1.5)
            for ccap in [bp['caps'][2*i], bp['caps'][2*i+1]]:
                ccap.set_color('black'); ccap.set_linewidth(2)
            median = bp['medians'][i]
            median.set_color(color); median.set_linewidth(2)

        ordered_labels = [_experiment_display_label(n) for n in exp_nums_present]
        centers = [exp_center_positions[lbl] for lbl in ordered_labels if lbl in exp_center_positions]
        tick_labels = [lbl for lbl in ordered_labels if lbl in exp_center_positions]
        ax.set_xticks(centers)
        ax.set_xticklabels(tick_labels, rotation=0)

        ax.set_xlabel('Experiment', fontsize=14)
        ax.set_ylabel('Number of Generation Iterations', fontsize=14)
        ax.tick_params(axis='x', labelsize=10.5)
        ax.tick_params(axis='y', labelsize=14)

        legend_patches = [Patch(facecolor=lighten_color(base_colors[c], 0.35), edgecolor=base_colors[c], label=lab) for c, lab in zip(cat_order, category_labels)]
        ax.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=len(cat_order), frameon=False, fontsize=15, columnspacing=1.0, handletextpad=0.4)

        # Fixed y-axis top limit at 10.1
        y_bottom = 0.9
        y_top_fixed = 10.1
        ax.set_ylim(bottom=y_bottom, top=y_top_fixed)
        ax.set_yticks(range(1, int(y_top_fixed) + 1))  # ticks 1..10 inclusive
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        ax.set_axisbelow(True)

        groups = [
            ('GPT 3.5 turbo', [_experiment_display_label(n) for n in range(1, 8)]),
            ('GPT 4.1 mini', [_experiment_display_label(n) for n in range(8, 13)]),
            ('GPT 5 mini', [_experiment_display_label(n) for n in range(13, 18)]),
        ]
        span_colors = ['#ffffff', '#f5f5f5', '#ffffff']

        ordered_labels = [lbl for lbl in tick_labels if lbl in exp_center_positions]
        ordered_centers = [exp_center_positions[lbl] for lbl in ordered_labels]
        base_gap = ordered_centers[1] - ordered_centers[0] if len(ordered_centers) >= 2 else 0.6
        boundaries = []
        for i, c in enumerate(ordered_centers):
            if i == 0:
                boundaries.append(c - base_gap / 2.0)
            else:
                prev = ordered_centers[i - 1]
                boundaries.append((prev + c) / 2.0)
        boundaries.append(ordered_centers[-1] + base_gap / 2.0)

        min_box_left = min(positions) - width / 2.0
        max_box_right = max(positions) + width / 2.0
        boundaries[0] = min_box_left
        boundaries[-1] = max_box_right

        label_to_span = {ordered_labels[i]: (boundaries[i], boundaries[i+1]) for i in range(len(ordered_labels))}

        # Draw shaded spans only (labels handled separately above axis)
        group_span_bounds = []
        for gi, (gname, glabels) in enumerate(groups):
            spans = [label_to_span[lbl] for lbl in glabels if lbl in label_to_span]
            if not spans:
                continue
            x_start = min(s[0] for s in spans)
            x_end = max(s[1] for s in spans)
            group_span_bounds.append((gname, x_start, x_end))
            ax.axvspan(x_start, x_end, color=span_colors[gi % len(span_colors)], zorder=0)

        gap_pad = 0.08
        ax.set_xlim(min_box_left - gap_pad, max_box_right + gap_pad)
        ax.margins(x=0)

        # Now place labels using axis-fraction coordinates above plot
        xmin, xmax = ax.get_xlim()
        for gname, x_start, x_end in group_span_bounds:
            center = (x_start + x_end) / 2.0
            x_frac = (center - xmin) / (xmax - xmin) if xmax > xmin else 0.5
            ax.text(x_frac, 1.012, gname, transform=ax.transAxes,
                    ha='center', va='bottom', fontsize=14, fontweight='bold',
                    color='#444', zorder=5, clip_on=False)

        sorted_centers = [exp_center_positions[lbl] for lbl in ordered_labels]
        for i in range(1, len(sorted_centers)):
            mid = (sorted_centers[i-1] + sorted_centers[i]) / 2.0
            ax.axvline(mid, color='grey', linestyle=':', linewidth=0.6, alpha=0.7)

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.20, top=0.92)
        out_path = os.path.join(out_dir, f'{args.prefix}_{dif}.pdf')
        plt.savefig(out_path, dpi=600, format='pdf')
        plt.close()

    # Optionally print where files were saved
    print('Saved boxplots to figures/:')
    for dif in difficulties:
        p = os.path.join(out_dir, f'{args.prefix}_{dif}.pdf')
        if os.path.isfile(p):
            print(f'  {p}')

