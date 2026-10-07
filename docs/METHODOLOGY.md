# Diabetes analysis methodology

## Outcome and analytic population

The label is the response to CDC DIQ010: whether a participant reports ever being told by a doctor or health professional that they have diabetes; the question excludes pregnancy-only diabetes where specified in the questionnaire. Code 1 maps to 1, code 2 to 0; borderline (3), refused (7), unknown (9) and missing responses do not enter binary modeling. No glucose or HbA1c diagnostic threshold is inferred. This is not a type-2-specific outcome. [CDC DIQ_J documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DIQ_J.htm)

The source workbook supplies 7,936 laboratory records. One-to-one left joins by SEQN add DIQ_J, DEMO_J and BMX_J from the identical 2017–2018 cycle. The original columns are retained unchanged. Restrict to age 20+: 5,265 adults. Exclude 163 borderline and 4 unknown/missing responses, leaving 5,098 adults (836 reported yes, 4,262 reported no). Row-level missing predictors remain missing before train-only imputation. Cohort and source-matching audits are exported.

## Predictors

The models use age, female indicator, BMI, urine ACR, urine creatinine, WBC count, hemoglobin, platelets, RDW and MCV. All seven laboratory features originate in the user's workbook. The demographics comparator uses only age, sex and BMI. IDs, questionnaire answers, treatment information and duplicate-unit fields are not predictors. Survey weights and design variables are retained for traceability but excluded from modeling.

## Evaluation

Stratify by the binary outcome into 60% train, 20% validation and 20% test with seed 42. Fit median imputation, missing indicators and standardization within a scikit-learn Pipeline on training records only. Logistic models use C=0.3, class_weight=balanced, max_iter=2000. Random forest uses 180 trees, maximum depth 6, minimum leaf size 12, balanced_subsample weights and seed 42. Hyperparameters are fixed, not tuned on test results.

Select the learned model with maximum validation average precision. For each learned model, choose a threshold by maximum validation balanced accuracy from 0.05 to 0.95 in increments of 0.01 (first threshold wins ties). Freeze all choices before evaluating the test set. The class-prior baseline uses 0.5. Report ROC AUC, average precision, precision, recall, F1, balanced accuracy, specificity, Brier score and confusion counts. Test curves are diagnostics, not a basis for subsequent tuning. The profile interface uses the evaluated training-only model and rejects input values outside observed training ranges.

## Descriptive analyses

Sidebar filters affect descriptive statistics and laboratory plots only. Raw observed measurements are used for these summaries. Variance and SD use n−1; Pearson r uses pairwise complete observations. IQR flags are statistical outliers, not diagnoses. Percentile line charts do not represent time. The historical six Matplotlib families, Seaborn heatmap and additional distributions remain available. CBC regression is supplementary and does not predict the diabetes label. Its complete-case eligibility is reported independently.

## Scope and uncertainty

No reported diagnosis is not proof of no disease. The sample may contain undiagnosed cases, reporting error and excluded borderline participants. Measurements may reflect existing disease and treatment; no causal or future-risk claims follow. Class-weighted scores are not calibrated clinical probabilities. Precision is limited at the selected threshold; false positives and negatives remain visible. One random split does not establish stable performance across hospitals, populations or time. This is a research prototype, with no external clinical validation.

Summaries are unweighted. Although the added demographic source contains WTMEC2YR/SDMVSTRA/SDMVPSU, survey-design inference has not been implemented. Do not label sample proportions as national prevalence. The original colorimetric strip reader is a separate proposed device with no image/calibration validation in this project.

## Sources

- User workbook: NHANES_2017-2018_Urinalysis_CBC_Dataset (1).xlsx, preserved in data/NHANES_2017_2018.xlsx.
- [CDC diabetes questionnaire](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DIQ_J.htm).
- [CDC demographics](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm): age, recorded sex, weight/design metadata.
- [CDC body measures](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BMX_J.htm): measured BMI.
- [CDC urine chemistry](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/ALB_CR_J.htm) and [CBC](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/CBC_J.htm): source laboratory definitions.

Download URLs, row counts and hashes are recorded in data/nhanes/sources.json. No raw source is modified during model preparation.
