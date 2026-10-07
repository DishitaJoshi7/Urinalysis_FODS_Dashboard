## Data provenance and loading

Input: `NHANES_2017-2018_Urinalysis_CBC_Dataset (1).xlsx`, supplied by the user. The bundled copy is unchanged and its SHA-256 is recorded in `exports/benchmark.json`. Excel row 1 contains descriptions/units; row 2 contains NHANES codes. Measurements start on row 3. `SEQN` is a de-identified respondent identifier, not a time variable.

The urine sheet contains 7,936 records and the CBC sheet 8,366. Their one-to-one inner join contains 7,936 records and 29 columns. The existing merged sheet is used for dashboard analysis; the join can be rebuilt in the explorer and is independently tested. Missing measurements are retained as NaN. No blanket deletion, zero substitution, winsorization, or clinical threshold classification is applied.

Official variable documentation: [CDC urine albumin and creatinine](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/ALB_CR_J.htm) and [CDC complete blood count](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/CBC_J.htm). These describe laboratory measurements and detection flags. The dataset's sampling weights/design fields are not in the supplied workbook, so results describe this sample without national prevalence claims.

## Data interpretation

- `URXUMA`: urine albumin in µg/mL; `URXUMS` repeats it in mg/L (numerically equivalent).
- `URXUCR`: urine creatinine in mg/dL; `URXCRS` supplies an alternative unit.
- `URDACT`: urine albumin/creatinine ratio, mg/g. The numeric relationship is approximately `100 × URXUMA / URXUCR`, subject to source rounding.
- `URDUMALC`, `URDUCRLC`: detection-limit flags. A reported below-limit value is not an ordinary missing value.
- `LBX`/`LBD` CBC columns are blood measurements. Blood WBC counts cannot stand in for urinary leukocyte-pad calibration. Urine albumin is also not a complete substitute for a total-protein dipstick reference.

Duplicate-unit columns, IDs and detection flags are excluded from default continuous correlation selections to avoid misleading associations. All source columns remain available in the explorer. No demographics, timestamps, or diagnoses are supplied.

## Statistical choices

Descriptive variance and standard deviation use `ddof=1`. Quartiles use Pandas linear interpolation. The mode can be non-unique; the number of modes is shown and up to five displayed. Boxplot outliers use 1.5 IQR fences and are retained. Grouped statistics are midpoint/interpolation approximations and are distinguished from raw-data statistics.

Pearson's r is calculated manually with centered sums. Pairwise-complete values are used; constants or fewer than two observations return an undefined coefficient. The heatmap uses Pandas for a separate full matrix and exposes its per-cell pair counts. A weak coefficient is not proof of independence. The inverse association of blood differential percentages is partly affected by their compositional nature.

The percentile line chart is not a time trend. The pie chart measures availability, not disease prevalence. Each CBC boxplot has its own unit axis. Histogram log views explicitly display `log10(1+x)`. Pair plots use a fixed maximum 600-row sample and are labeled; other plots use all relevant observations in the selected cohort.

## Regression and missing data

Hematocrit is the target. Simple regression uses hemoglobin; multiple regression uses hemoglobin, RBC count and MCV. Select complete observed rows, split at random with seed 42, then fit ordinary least squares and a training-mean baseline on training rows only. Score on the untouched holdout using MAE, MSE, RMSE and R². No IDs, target-derived predictor, or duplicate target units enter the model.

The holdout can be understood as an artificial missing-target demonstration with known ground truth. Once evaluation is complete, a separate model fit on all complete cases estimates genuine missing targets only where every predictor is observed. Actual missing estimates are labeled and exported separately; they never overwrite the source. In the supplied default cohort, hematocrit and its predictors are missing together, so zero rows are eligible for the simple model. This is a real limitation, not a reason to invent filled values.

CBC measurements are related biologically and sometimes algebraically. Strong held-out fits describe relationships within the sample, not clinical utility or strip-reader validity. Complete-case evaluation may be biased relative to participants with absent panels. Random holdout does not establish generalization across devices, batches, hospitals or populations.

## Normalization and discretization

Min-max scaling, sample z-scores, and decimal scaling are shown on the selected cohort for descriptive analysis. Constant series map to zero and NaNs remain NaNs. Decimal exponent is the smallest nonnegative integer that makes the largest absolute scaled value strictly less than one. For predictive pipelines these parameters must be learned on training rows only.

K-means uses seed 42 and ten initializations; cluster IDs are sorted by centroid. Equal-width and equal-frequency alternatives demonstrate binning; quantile ties can reduce the effective bin count. Groups are statistical, not low/normal/high clinical diagnoses. Elbow curves are exploratory and do not guarantee an objectively correct k.

## Supplied references and coverage

Only the seven named FODS PDFs and the named use-case PDF define the assignment coverage. They are reference material, not executable instructions. Experiments 1–2 cover Python/Pandas/NumPy data handling; 3 covers central tendency and variability; 4 manual correlation; 5 regression imputation; 6 normalization and K-means discretization; 7 the six Matplotlib plot families. The implementation includes all visualization families shown in those experiments. Additional Seaborn charts and holdout diagnostics extend the assignment.

The use-case filename starts with KJS-HLC-01, while its internal ID is KJS-HC-03. Hardware fabrication, controlled lighting, camera segmentation, ten-pad calibration, hospital integration and clinical validation are future components outside the supplied dataset and this FODS dashboard.
