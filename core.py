"""Data preparation and course calculations, independent of the dashboard UI."""
from pathlib import Path
import math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Resolve paths relative to this file so VS Code can launch from any directory.
ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / 'data' / 'NHANES_2017_2018.xlsx'
FLAGS = ['URDUMALC', 'URDUCRLC']
UNITS_DUPLICATES = ['URXUMS', 'URXCRS']
DEFAULT_FEATURES = ['URXUMA', 'URXUCR', 'URDACT', 'LBXWBCSI', 'LBXRBCSI',
                    'LBXHGB', 'LBXHCT', 'LBXMCVSI', 'LBXPLTSI']


def read_workbook(source=DATA_PATH):
    """Use Excel row 2 as variable names; row 1 is the human-readable dictionary."""
    book = pd.ExcelFile(source)
    sheets = {}
    labels = {}
    for name in ['Urine_Albumin_Creatinine', 'Complete_Blood_Count', 'Merged_Dataset']:
        raw = pd.read_excel(book, sheet_name=name, header=None)
        codes = raw.iloc[1].astype(str).str.strip().tolist()
        labels.update(dict(zip(codes, raw.iloc[0].astype(str))))
        frame = raw.iloc[2:].copy()
        frame.columns = codes
        # Coercion keeps missing measurements as NaN; zeros remain genuine zeros.
        frame = frame.apply(pd.to_numeric, errors='coerce').reset_index(drop=True)
        if frame.SEQN.isna().any() or frame.SEQN.duplicated().any():
            raise ValueError(f'{name}: SEQN must contain unique, nonmissing respondent IDs.')
        frame['SEQN'] = frame.SEQN.astype('int64')
        sheets[name] = frame
    return sheets, labels


def measurement_columns(df):
    """IDs and detection flags are not continuous laboratory measurements."""
    return [c for c in df.columns if c not in ['SEQN'] + FLAGS + UNITS_DUPLICATES]


def summary_table(df, columns):
    """Exp 3: sample variance/SD use n-1; quartiles use linear interpolation."""
    records = []
    for c in columns:
        s = df[c].dropna()
        modes = s.mode()
        q1, q3 = s.quantile([.25, .75]) if len(s) else (np.nan, np.nan)
        records.append(dict(Variable=c, Observed=len(s), Missing=int(df[c].isna().sum()),
            Mean=s.mean(), Median=s.median(), Mode=', '.join(f'{v:g}' for v in modes[:5]),
            Modes=len(modes), Minimum=s.min(), Maximum=s.max(), Range=s.max()-s.min(),
            Variance=s.var(ddof=1), SD=s.std(ddof=1), Q1=q1, Q3=q3, IQR=q3-q1,
            IQR_outliers=int(((s < q1-1.5*(q3-q1)) | (s > q3+1.5*(q3-q1))).sum())))
    return pd.DataFrame(records)


def manual_pearson(x, y):
    """Exp 4: compute Pearson's r from centered sums, without corr/corrcoef."""
    pairs = pd.DataFrame({'x': x, 'y': y}).replace([np.inf, -np.inf], np.nan).dropna()
    xs, ys = pairs.x.tolist(), pairs.y.tolist()
    n = len(xs)
    if n < 2:
        return float('nan'), n
    mx, my = sum(xs)/n, sum(ys)/n
    dx, dy = [v-mx for v in xs], [v-my for v in ys]
    denominator = math.sqrt(sum(v*v for v in dx) * sum(v*v for v in dy))
    return (sum(a*b for a, b in zip(dx, dy))/denominator if denominator else float('nan')), n


def normalization(s):
    """Exp 6: compare original, min-max, sample z-score, and decimal scaling."""
    s = s.astype(float)
    spread, sd, maximum = s.max()-s.min(), s.std(ddof=1), s.abs().max()
    power = max(0, math.floor(math.log10(maximum))+1) if pd.notna(maximum) and maximum > 0 else 0
    # Constant series map to zero; a missing input stays missing.
    zeros = s * 0
    return pd.DataFrame({'Original': s, 'Min-max': (s-s.min())/spread if spread else zeros,
        'Z-score': (s-s.mean())/sd if pd.notna(sd) and sd > 0 else zeros,
        'Decimal': s/(10**power)}), power


def discretize(s, bins=3, method='K-means'):
    """Return observed values with ordered bin IDs, preserving original row indices."""
    observed = s.dropna()
    if observed.nunique() < bins:
        raise ValueError(f'At least {bins} distinct observed values are required.')
    if method == 'K-means':
        model = KMeans(n_clusters=bins, n_init=10, random_state=42)
        raw_labels = model.fit_predict(observed.to_numpy().reshape(-1, 1))
        centers = model.cluster_centers_.ravel()
        order = np.argsort(centers)
        ranks = {old: new+1 for new, old in enumerate(order)}
        labels = np.array([ranks[i] for i in raw_labels])
        edges = np.sort(centers)
    else:
        if method == 'Equal width':
            cat, edges = pd.cut(observed, bins=bins, retbins=True, duplicates='drop')
        else:
            cat, edges = pd.qcut(observed, q=bins, retbins=True, duplicates='drop')
        labels = cat.cat.codes.to_numpy()+1
    return pd.DataFrame({'Value': observed, 'Bin': labels}, index=observed.index), edges


def grouped_stats(s, bins=8):
    """Midpoint approximation for grouped data, alongside explicit interval edges."""
    values = s.dropna().to_numpy()
    if len(values) < 2:
        raise ValueError('Two observed values are required.')
    counts, edges = np.histogram(values, bins=bins)
    mids = (edges[:-1]+edges[1:])/2
    n = int(counts.sum())
    mean = np.dot(counts, mids)/n
    variance = np.dot(counts, (mids-mean)**2)/(n-1)
    cumulative = counts.cumsum()
    def quantile(p):
        i = min(int(np.searchsorted(cumulative, p*n)), len(counts)-1)
        before = cumulative[i-1] if i else 0
        return edges[i] + ((p*n-before)/counts[i])*(edges[i+1]-edges[i])
    i = int(np.argmax(counts))
    prev = counts[i-1] if i else 0
    nxt = counts[i+1] if i+1 < bins else 0
    d1, d2 = counts[i]-prev, counts[i]-nxt
    mode = edges[i]+d1/(d1+d2)*(edges[i+1]-edges[i]) if d1+d2 else mids[i]
    table = pd.DataFrame({'Lower': edges[:-1], 'Upper': edges[1:], 'Midpoint': mids,
                          'Frequency': counts, 'Cumulative': cumulative})
    stats = {'Grouped mean': mean, 'Grouped median': quantile(.5), 'Grouped mode': mode,
             'Grouped variance': variance, 'Grouped SD': math.sqrt(variance),
             'Grouped IQR': quantile(.75)-quantile(.25)}
    return table, stats


def regression_experiment(df, features, target='LBXHCT', test_size=.2):
    """Exp 5: score unseen observed rows, then estimate eligible missing targets.

    The holdout is equivalent to hiding known target values, so it is evaluable.
    Real missing targets have no ground truth. They are never used to score a model.
    Complete predictors are required; we do not silently fill absent blood panels.
    """
    if target in features or 'SEQN' in features or not features:
        raise ValueError('Choose predictors that exclude the target and respondent ID.')
    known = df.dropna(subset=features+[target])
    if len(known) < 30:
        raise ValueError('At least 30 complete rows are required for a stable teaching split.')
    if known[target].nunique() < 2:
        raise ValueError('The target must vary.')
    train, test = train_test_split(known, test_size=test_size, random_state=42)
    model = LinearRegression().fit(train[features], train[target])
    baseline = DummyRegressor(strategy='mean').fit(train[features], train[target])
    pred = model.predict(test[features])
    base = baseline.predict(test[features])
    score_rows = []
    for name, prediction in [('Linear regression', pred), ('Training-mean baseline', base)]:
        score_rows.append({'Model': name, 'MAE': mean_absolute_error(test[target], prediction),
            'MSE': mean_squared_error(test[target], prediction),
            'RMSE': math.sqrt(mean_squared_error(test[target], prediction)),
            'R2': r2_score(test[target], prediction)})
    results = test[['SEQN', target]].rename(columns={target:'Observed'}).copy()
    results['Predicted'] = pred
    results['Residual'] = results.Observed-results.Predicted
    # Refit on all complete observed cases only after holdout metrics are frozen.
    final_model = LinearRegression().fit(known[features], known[target])
    missing = df.loc[df[target].isna() & df[features].notna().all(axis=1), ['SEQN']+features].copy()
    missing['Estimated_'+target] = final_model.predict(missing[features]) if len(missing) else pd.Series(dtype=float)
    missing['Status'] = 'Regression estimate; not measured'
    return dict(metrics=pd.DataFrame(score_rows), predictions=results, missing=missing,
        train=train, test=test, model=model, final_model=final_model, features=features,
        target=target, observed=len(known), excluded=len(df)-len(known),
        unfilled=int(df[target].isna().sum())-len(missing))


def arff_text(df, relation='nhanes_coursework'):
    """Weka numeric ARFF: missing values are ?, and target must be last for regression."""
    lines = [f'@RELATION {relation}', '']
    for col in df:
        lines.append(f'@ATTRIBUTE {col} NUMERIC')
    lines += ['', '@DATA']
    for row in df.itertuples(index=False, name=None):
        lines.append(','.join('?' if pd.isna(v) else format(float(v), '.12g') for v in row))
    return '\n'.join(lines)+'\n'
