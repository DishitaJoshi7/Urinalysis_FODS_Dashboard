"""Matplotlib and Seaborn plots used throughout the FODS dashboard."""
import matplotlib
matplotlib.use('Agg')  # A noninteractive backend works in browsers and automated tests.
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from core import manual_pearson

# Keep colors and typography consistent across charts and exported PNGs.
TEAL, NAVY, GOLD, CORAL = '#14877e', '#243c59', '#d49a38', '#c86555'
PALETTE = [TEAL, NAVY, GOLD, CORAL, '#8b79ac', '#799aab']
sns.set_theme(style='whitegrid', palette=PALETTE, font='DejaVu Sans',
              rc={'axes.spines.top': False, 'axes.spines.right': False,
                  'axes.labelcolor': NAVY, 'text.color': NAVY, 'grid.alpha': .22})


def canvas(w=7, h=4):
    return plt.subplots(figsize=(w, h), layout='constrained')


def distribution(s, label, bins=30, log=False):
    """Use log10(1+x) only when explicitly requested; label the transformed scale."""
    values = s.dropna()
    fig, ax = canvas()
    if log:
        values = np.log10(1+values[values >= 0])
        label = 'log10(1 + '+label+')'
    sns.histplot(values, bins=bins, kde=values.nunique()>1, ax=ax, color=TEAL, edgecolor='white')
    if len(values):
        ax.axvline(values.median(), color=CORAL, ls='--', label=f'Median {values.median():.2f}')
        ax.legend(frameon=False)
    ax.set(xlabel=label, ylabel='Number of records')
    return fig


def scatter(df, x, y, labels, trend=True):
    """Pairwise complete observations determine both the plotted points and r."""
    clean = df[[x, y]].dropna() if x != y else df[[x]].dropna()
    fig, ax = canvas()
    ax.scatter(clean[x], clean[y], s=10, alpha=.25, color=TEAL, rasterized=True)
    r, n = manual_pearson(df[x], df[y])
    if trend and len(clean) >= 2 and clean[x].nunique()>1:
        slope, intercept = np.polyfit(clean[x], clean[y], 1)
        xx = np.array([clean[x].min(), clean[x].max()])
        ax.plot(xx, slope*xx+intercept, color=CORAL, lw=2, label='Least-squares trend')
        ax.legend(frameon=False)
    ax.set(xlabel=labels.get(x,x), ylabel=labels.get(y,y), title=f'Pearson r = {r:.3f}   |   n = {n:,}')
    return fig


def missingness(df):
    """Show missing fractions with the full selected cohort as denominator."""
    pct = df.drop(columns='SEQN', errors='ignore').isna().mean().mul(100).sort_values().tail(12)
    fig, ax = canvas(7, 4.7)
    ax.barh(pct.index, pct.values, color=TEAL)
    ax.set(xlabel='Missing measurements (%)', xlim=(0, max(12, pct.max()*1.3)))
    for i, v in enumerate(pct):
        ax.text(v+.15, i, f'{v:.1f}%', va='center', fontsize=9)
    return fig


def six_plots(df, labels, selected='LBXHGB', bins=25):
    """Exp 7: all six required techniques with real data and meaningful axes."""
    s = df[selected].dropna()
    figures = []
    # Percentiles provide an ordered x-axis without inventing time-series data.
    fig, ax = canvas()
    q = np.linspace(.05, .95, 19)
    ax.plot(q*100, s.quantile(q), marker='o', markersize=4, color=TEAL)
    ax.set(xlabel='Percentile', ylabel=labels[selected])
    figures.append(('Line plot', fig, 'Values across percentiles; the horizontal axis is not time.'))
    # Differential percentages share one unit, making bar heights comparable.
    cols = ['LBXLYPCT','LBXMOPCT','LBXNEPCT','LBXEOPCT','LBXBAPCT']
    means = df[cols].dropna().mean()
    fig, ax = canvas()
    bars = ax.bar(['Lymph.','Mono.','Neut.','Eosin.','Baso.'], means, color=PALETTE[:5])
    ax.bar_label(bars, fmt='%.1f', padding=3)
    ax.set(ylabel='Mean differential (%)', ylim=(0, max(70, means.max()*1.2)))
    figures.append(('Bar plot', fig, 'Mean WBC differential percentages on complete differential panels.'))
    figures.append(('Scatter plot', scatter(df,'LBXHGB','LBXHCT',labels),
                    'Each point is a respondent with both measurements. A trend is association, not causation.'))
    # Availability is a defensible categorical split without imposing clinical thresholds.
    fig, ax = canvas()
    counts = [int(df[selected].notna().sum()), int(df[selected].isna().sum())]
    ax.pie(counts, labels=['Observed','Missing'], autopct='%1.1f%%', startangle=90,
           colors=[TEAL, '#dae4e8'], wedgeprops={'edgecolor':'white','linewidth':2})
    ax.set(aspect='equal')
    figures.append(('Pie plot', fig, f'Measurement availability for {selected}; denominator = {len(df):,} records.'))
    fig, ax = canvas()
    if len(s):
        ax.boxplot(s, orientation='horizontal', patch_artist=True, boxprops={'facecolor':'#b9ddd6'},
                   medianprops={'color':CORAL}, flierprops={'markersize':3,'alpha':.3})
    ax.set(xlabel=labels[selected], yticks=[])
    figures.append(('Box plot', fig, 'The box spans Q1–Q3; whiskers extend to the last values within 1.5 IQR.'))
    figures.append(('Histogram', distribution(s,labels[selected],bins),
                    f'Counts in {bins} value intervals; the dashed line marks the median.'))
    return figures
