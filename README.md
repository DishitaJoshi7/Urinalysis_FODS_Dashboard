# Diabetes Analyzer — NHANES Laboratory Analytics

An interactive Python dashboard that uses the supplied NHANES 2017–2018 urine/CBC workbook to explore and classify **self-reported doctor-told diabetes status** in adults aged 20+. It uses Matplotlib, Seaborn and scikit-learn, with commented source code and a VS Code workspace.

## Research question

Can age, recorded sex, BMI and the available urine/blood measurements distinguish adults reporting a diabetes diagnosis from adults reporting no diagnosis? Does adding the supplied laboratory data improve held-out discrimination compared with demographics alone?

This is current-status classification, not future-risk forecasting, type-2-specific classification, clinical diagnosis or strip-color analysis. The negative label means **no reported diagnosis**, not confirmed absence of diabetes.

## Data and outcome

The original workbook is preserved at `data/NHANES_2017_2018.xlsx`. Its merged sheet contains **7,936 respondents and 29 original columns**. Matching public CDC files are included under `data/nhanes/`:

| Source | Role | Documentation |
|---|---|---|
| User-supplied urine/CBC workbook | Original laboratory predictors | [Urine chemistry](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/ALB_CR_J.htm), [CBC](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/CBC_J.htm) |
| DIQ_J | Diabetes question DIQ010 supplies the label | [CDC DIQ codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DIQ_J.htm) |
| DEMO_J | Age, recorded sex, and survey-design metadata | [CDC demographics](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm) |
| BMX_J | Measured BMI | [CDC body measures](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BMX_J.htm) |

Files are left-joined one-to-one by `SEQN`. Include age 20+ with DIQ010 equal to 1 (yes) or 2 (no); exclude borderline, refused, unknown and missing responses. This yields **5,098 adults: 836 positive and 4,262 negative**. The model does not use DIQ010 itself as a predictor, diabetes medications, diagnosis history, IDs, duplicate units or survey weights. Source URLs and SHA-256 checksums are in `data/nhanes/sources.json` and `exports/diabetes/benchmark.json`.

## Run in VS Code

Open this folder or `Urinalysis_FODS.code-workspace`. The workspace filename is retained for compatibility with the existing project.

First-time setup (Python 3.12):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If your environment is already installed, **only the last command is needed**. Open the Local URL printed in the terminal, usually http://localhost:8501. Keep the terminal running. Ctrl+C stops the server. After an update, stop and restart the server to load new pages and data. No new dependencies are required for the diabetes update.

The included `setup_and_run.cmd` also performs setup and launch. Select the `.venv` interpreter in VS Code and press F5 for the included debugger launch. PowerShell activation is unnecessary. For a busy port, append `--server.port 8502`. On macOS/Linux, use `python3.12` and `.venv/bin/python` equivalents. All source data is local; no online data fetch is performed by the dashboard.

## Dashboard views

| View | Result |
|---|---|
| Overview | Reported-status counts, urine ACR comparisons, descriptive group statistics |
| Data explorer | Joined measurements, missingness, data dictionary and cohort/merge audits |
| Model performance | Baselines, validation selection, test ROC/PR curves, confusion matrix, precision/recall/F1, reliability diagram |
| Research profile score | Complete illustrative profile scored by the evaluated classifier; no diagnosis or personal data storage |
| Descriptive statistics | Mean, median, modes, sample variance/SD, grouped frequencies, IQR and boxplots |
| Correlation | Manual Pearson calculation, relationship plots and heatmap |
| CBC regression | Supplementary hematocrit regression/imputation analysis; separate from the diabetes classifier |
| Normalization & clustering | Min-max, sample z-score, decimal scaling, K-means and interval binning |
| Visualizations | All six original plot families, plus violin, ECDF and pair plots |
| Data & model exports | Classification CSV/ARFF files and measured Python results |

Sidebar status/age filters affect descriptive views. **The models always use the same full eligible cohort and frozen splits**; filtering to one response group cannot silently change the classification evaluation. Viva coaching and programming tutorials are not displayed; code comments remain.

## Model design

- Stratified **60/20/20** split, seed 42: **3,058 train / 1,020 validation / 1,020 test**.
- Demographic features: age, recorded sex (female indicator), BMI.
- Original workbook features: urine ACR, urine creatinine, WBC count, hemoglobin, platelet count, red-cell distribution width and mean cell volume.
- Compare a class-prior baseline, demographics logistic regression, lab-plus-demographics logistic regression, and lab-plus-demographics random forest.
- Median imputation (with missing indicators) and standardization are fit on training rows only. Class weighting is used for the learned classifiers; no oversampling is performed before splitting.
- Model selection uses validation **average precision**. Each model's classification threshold maximizes validation balanced accuracy over 0.05–0.95, step 0.01. The baseline uses 0.5.
- Evaluate on the untouched test split after those choices. No holdout tuning or refitting on test observations. Profile scoring uses the same training-only model that was evaluated.

## Measured Python results

Validation selected **Labs + demographics forest**. Test results at frozen thresholds:

| Model | ROC AUC | Average precision | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| Class-prior baseline | 0.500 | 0.164 | 0.000 | 0.000 | 0.000 |
| Demographics logistic | 0.790 | 0.412 | 0.307 | 0.820 | 0.447 |
| Labs + demographics logistic | 0.804 | 0.440 | 0.308 | 0.808 | 0.446 |
| Labs + demographics forest | 0.820 | 0.488 | 0.328 | 0.784 | 0.463 |

The selected forest's threshold is **0.46**. Test confusion counts: **585 true negatives, 268 false positives, 36 false negatives and 131 true positives**. Precision is about 33%, so most positive classifications are false positives at this operating point. The majority-class baseline achieves about 84% accuracy while identifying zero positive cases; accuracy alone is unsuitable here. These are exploratory sample results, not clinical validation.

The added laboratory features modestly improve observed test discrimination over demographics alone. This single split does not prove a statistically significant or clinically useful improvement. The reliability diagram and Brier score expose imperfect calibration; class-weighted model scores are not validated personal probabilities.

## RapidMiner and Weka

**Prepared, not executed.** The new classification inputs are in `exports/diabetes/`, separate from the older CBC regression exports.

- `train.csv`, `validation.csv`, `test.csv`: ten predictors plus a nominal `yes`/`no` target, with missing inputs filled from **training medians only**.
- Corresponding `.arff` files use nominal `{no,yes}` class labels, so Weka performs classification rather than regression.
- `*_raw.csv` files preserve missing values. `*_ids.csv` files preserve audit IDs separately from predictors.
- `tools/rapidminer_diabetes.rmp`: decision-tree classification process template. Update CSV paths before importing/running.
- `tools/run_weka_diabetes.cmd`: Weka Logistic classifier command; supply your installed `weka.jar` path.

These files share Python's split membership but the external-tool preprocessing/models are not exact replicas of the Python pipelines (which also use missing indicators and class weights). Do not claim matching scores. See [tool instructions](docs/RAPIDMINER_WEKA.md). External-tool metrics will be added only after actual execution.

## Files and reproducibility

`app.py` handles navigation and filters; `diabetes.py` owns joins, target coding, training and exports; `diabetes_ui.py` caches source data and model results. Original laboratory calculations remain in `core.py`, charts in `charts.py`, and UI pages in `app_pages/`. The input workbook is unchanged. `prepare_diabetes.py` regenerates classification exports; `prepare_exports.py` remains the separate CBC regression exporter.

```powershell
.\.venv\Scripts\python.exe prepare_diabetes.py
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

Raw CDC downloads are included; `download_diabetes_sources.py` reproduces the downloads when network access is available. Rebuilding with changed data or library versions may change results. Pinned versions are in `requirements.txt`.

## Limitations and original use case

Self-report does not identify undiagnosed diabetes and does not reliably distinguish diabetes types. Cross-sectional lab measurements can reflect disease duration, treatment and complications; they cannot establish that a model predicts future onset. Borderline responses are excluded, which narrows applicability. There is no external or prospective validation.

The merged demographic file contains survey weights/design variables, but this project deliberately reports **unweighted sample summaries and model metrics**. It does not estimate U.S. prevalence or use the survey design for population inference. Age 80 is top-coded to mean 80 or older. Neither sex-specific clinical thresholds nor disease diagnoses are assigned.

The original PDF describes a urine-strip colorimetry device. This project now studies diabetes-status associations in the related laboratory data; it does **not** implement or validate that device. No RGB images or paired calibration concentrations are available.

## Project status

Last updated: **8 October 2026**. The Project methodology page has been removed from dashboard navigation. The diabetes data, analysis views, classification pipelines and CSV/ARFF exports are implemented. See `docs/VALIDATION.md` for checks actually completed. RapidMiner/Weka native execution remains pending. The README is maintained alongside subsequent project changes.

To update an already-connected GitHub repository, review the changed/new files in Source Control, stage, commit, then push/sync. Local edits do not automatically update GitHub.
