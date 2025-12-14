import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
import numpy as np
import seaborn as sns
import matplotlib.colors as mcolors

# 0 no change
def lighten_color(color, amount=0.2):
    rgb = np.array(mcolors.to_rgb(color), dtype=float)
    white = np.array([1.0, 1.0, 1.0], dtype=float)
    blended = (1 - amount) * rgb + amount * white
    blended = np.clip(blended, 0.0, 1.0)
    return mcolors.to_hex(tuple(blended))

def create_graphics(experiments, custom_labels=None):
    """
    df is a dataframe containing columns:
    experiment,difficulty,failure,valid,complete,complete_gt
    each 'experiment' has three entries, one for each difficulty: easy,medium,hard
    failure,valid,complete,complete_gt are integers

    Args:
        experiments: list of experiment IDs (e.g., ['exp1', 'exp2', 'exp3'])
        custom_labels: optional list of custom labels for each experiment (same length as experiments)
                      Use None for any experiment to fall back to the default label
    """
    df = pd.read_csv('exp_results/grouped_data_classification_only.csv')

    # Mapping experiment data -> label shown
    experiment_names = {
        # gpt 3.5 turbo
        'exp1': 'E1: SpecGen\nnon-null/no ovf asm',
        'exp2': 'E2: OG Prompt\nnon-null/no ovf asm',

        'exp3': 'E3: SpegGen',
        'exp4': 'E4: OG prompt',
        'exp5': 'E5: strict prompt',
        'exp6': 'E6: OG prompt + EC',
        'exp7': 'E7: strict prompt + EC',
        # gpt 4.1 mini
        'exp8': 'E8: SpegGen',
        'exp9': 'E9: OG prompt',
        'exp10': 'E10: strict prompt',
        'exp11': 'E11: OG prompt + EC',
        'exp12': 'E12: strict prompt + EC',
        # gpt 5 mini
        'exp13': 'E13: SpegGen',
        'exp14': 'E14: OG prompt',
        'exp15': 'E15: strict prompt',
        'exp16': 'E16: OG prompt + EC',
        'exp17': 'E17: strict prompt + EC',
    }

    # Override with custom labels if provided
    if custom_labels is not None:
        if len(custom_labels) != len(experiments):
            raise ValueError(f"custom_labels length ({len(custom_labels)}) must match experiments length ({len(experiments)})")
        for exp, custom_label in zip(experiments, custom_labels):
            if custom_label is not None:
                experiment_names[exp] = custom_label

    difficulties = ['easy', 'medium', 'hard']
    categories = ['failure', 'valid', 'complete', 'complete_gt']

    # okabe ito color palette for color blindness
    categories_colors = ["#d55e00", "#f0e442", "#0072b2", "#009e73"]
    categories_colors = [lighten_color(c, 0.3) for c in categories_colors]

    num_samples_by_difficulty = {
        'easy': 140,
        'medium': 160,
        'hard': 20
    }

    # Make a 100% stacked bar chart
    # The stacks must be in the following order (bottom to top):
    # failure, valid, complete, complete_gt

    # Divide in three sections, one for each difficulty, in the following order: easy, medium, hard
    # Each section must contain the respective entry for each experiment

    # Do not add one label per chart. Instead, make a single label at the bottom,
    # containing the color-category label.

    # In the middle of each stack, add a label with the percentage, with 1 decimal place.
    # Show every percentage, except the ones below the threshold:
    PERCENTAGE_LABEL_THRESHHOLD=3.7

    # Outside-percentage annotation controls (for values below threshold)
    OUTSIDE_LABEL_OFFSET_POINTS = 6   # horizontal gap from bar edge (in points)
    OUTSIDE_LABEL_FONT_SIZE = 18
    OUTSIDE_LABEL_FONT_WEIGHT = 'regular'
    OUTSIDE_ARROW_STYLE = '-'
    OUTSIDE_ARROW_COLOR = '#444444'
    OUTSIDE_ARROW_LINEWIDTH = 0.8
    OUTSIDE_LABEL_SIDE = 'right'   # 'right' or 'left'
    OUTSIDE_LABEL_Y_OFFSET_POINTS = 18  # vertical offset (points) for outside labels; alternates -Y,0,Y this value

    # Make bars thicker (0<width<=1; 1 means bars touch)
    BAR_WIDTH = 0.65

    # Legend spacing controls (increase these to add more gap)
    LEGEND_Y_OFFSET = -0.06        # more negative -> legend lower
    LEGEND_BORDERAXESPAD = 1.4    # bigger -> more gap between axes and legend
    BOTTOM_MARGIN = 0.30          # bigger -> more space reserved at bottom

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
        'failure': 'Failure',
        'valid': 'Valid',
        'complete': 'Complete',
        'complete_gt': 'Complete GT',
    }

    # Create subplots: one column per difficulty
    n_sections = len(difficulties)
    fig, axes = plt.subplots(1, n_sections, figsize=(18, 8), sharey=True)

    if n_sections == 1:
        axes = [axes]

    # Plot each difficulty section
    for ax, diff in zip(axes, difficulties):
        # Filter and order by experiment
        sub = (
            df[df['difficulty'] == diff]
            .set_index('experiment')
            .reindex(list(experiments))
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
        # Alternate vertical offset for each outside arrow in this section
        arrow_index = 0

        # Stacked bars in required order (failure, valid, complete, complete_gt)
        for cat, color in zip(categories, categories_colors):
            heights = percs[cat].to_numpy()
            bars = ax.bar(
                x, heights, bottom=bottoms, width=width,
                color=color, edgecolor='white', linewidth=0.6
            )

            # Percentage labels: inside if >= threshold, otherwise outside with arrow
            for rect, h, b in zip(bars, heights, bottoms):
                if h >= PERCENTAGE_LABEL_THRESHHOLD:
                    ax.text(
                        rect.get_x() + rect.get_width() / 2.0,
                        b + h / 2.0,
                        f"{h:.1f}%",
                        ha='center', va='center',
                        fontsize=22, fontweight='regular', color='black',
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
                    # Alternate Y offset: -Y, 0, Y, ...
                    y_sign = -1 if (arrow_index % 3 == 0) else 0 if (arrow_index % 3 == 1) else 1
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
            arrow_index += 1
            bottoms += heights

        # X ticks as experiment short names
        ax.set_xticks(x, [experiment_names.get(e, e) for e in sub['experiment']])

        if ROTATE_XTICK_LABELS:
            # Slant labels to improve readability for long names
            plt.setp(ax.get_xticklabels(),
                     rotation=XTICK_LABEL_ROTATION,
                     ha=XTICK_LABEL_HALIGN,
                     rotation_mode='anchor')
        # Font size for experiment names
        ax.tick_params(axis='x', labelsize=20)
        # Font size for Y axis ticks
        ax.tick_params(axis='y', labelsize=20)

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
        title = f"{diff.capitalize()} (n={n})" if n is not None else diff.capitalize()
        ax.set_title(title, pad=10, fontsize=20, fontweight='regular')

        # Clean look
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)

    axes[0].set_ylabel('% of samples with result', fontsize=18)

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
        handletextpad=0.6,    # spacing inside legend
        labelspacing=0.6,     # spacing inside legend
        fontsize=22           # category labels font size
    )

    plt.subplots_adjust(bottom=BOTTOM_MARGIN, wspace=0.15)
    #plt.tight_layout()

    exp_nums = [e[3:] if isinstance(e, str) and e.startswith('exp') else str(e) for e in experiments]
    fig_name = f"{'_'.join(exp_nums)}.pdf"

    fig.savefig(f'figures/{fig_name}', dpi=600, bbox_inches='tight', format='pdf')
    plt.close()
    #plt.show()

if __name__ == '__main__':
    #1. impact of the mutation:		 {1,2,3} {7,8} {12,13}	
    #2. impact of the prompt		 {3,4} {5,6} {8,9} {10,11} {13,14} {15,16}	
    #3. impact of the embedded compl {3,5} {4,6} {8,10} {9,11} {13, 15} {14 16}
    #4. changed accross models		 {2,7,12} {3,8,13} {4,9,14} {5,10,15} {6,11,16}

    # Format: each item can be either:
    #   - a list of experiment IDs (uses default labels)
    #   - a tuple of (experiment_list, custom_labels_list)
    all_experiments_comparisons = [
        # reproducibility
        ['exp1', 'exp2'],

        #arith non vs no arith null
        ['exp1', 'exp3'],
        ['exp2', 'exp4'],

        # SpecGen and mutation, gpt 3.5 turbo
        ['exp3', 'exp4'],
        ['exp8', 'exp9'],
        ['exp13', 'exp14'],

        #2. impact of the prompt
        ['exp4', 'exp5'],
        ['exp6', 'exp7'],
        ['exp9', 'exp10'],
        ['exp11', 'exp12'],
        ['exp14', 'exp15'],
        ['exp16', 'exp17'],

        #3. impact of the embedded completeness
        ['exp4', 'exp6'],
        ['exp5', 'exp7'],
        ['exp9', 'exp11'],
        ['exp10', 'exp12'],
        ['exp14', 'exp16'],
        ['exp15', 'exp17'],

        # 4. changed accross models
        (['exp3', 'exp8', 'exp13'], ['E3: GPT-3.5 turbo', 'E8: GPT-4.1 mini', 'E13: GPT-5 mini']),
        (['exp4', 'exp9', 'exp14'], ['E4: GPT-3.5 turbo', 'E9: GPT-4.1 mini', 'E14: GPT-5 mini']),
        (['exp5', 'exp10', 'exp15'], ['E5: GPT-3.5 turbo', 'E10: GPT-4.1 mini', 'E15: GPT-5 mini']),
        (['exp6', 'exp11', 'exp16'], ['E6: GPT-3.5 turbo', 'E11: GPT-4.1 mini', 'E16: GPT-5 mini']),
        (['exp7', 'exp12', 'exp17'], ['E7: GPT-3.5 turbo', 'E12: GPT-4.1 mini', 'E17: GPT-5 mini'])
    ]

    for item in all_experiments_comparisons:
        # Check if item is a tuple/list with custom labels or just a list of experiments
        if isinstance(item, tuple) and len(item) == 2:
            exp_tuple, custom_labels = item
            create_graphics(exp_tuple, custom_labels)
        else:
            # Just a list of experiments, use default labels
            create_graphics(item)
