# Validation results

Validated on 8 October 2026 using Python 3.12 and the pinned project dependencies.

## Completed checks

- **28 tests passed** across three runs: 5 diabetes data/model/export checks, 14 dashboard page/interaction checks, and 9 original laboratory calculation checks.
- Before the methodology page was removed from navigation, all 11 dashboard pages completed under Streamlit AppTest without application exceptions. Interactions covered status filtering, alternative binning, ECDF selection, multiple CBC regression, profile submission, and unchanged model evaluation when descriptive filters change.
- The latest supplied workbook's merged table exactly matches the included workbook. Original laboratory columns and missing values are preserved in the enriched join.
- Source table: 7,936 respondents. Eligible adult cohort: 5,098, comprising 836 reported-diabetes responses and 4,262 no-diagnosis responses. Borderline and unavailable responses are excluded.
- Stratified train/validation/test membership has no overlapping respondent IDs. Imputer statistics are derived only from training observations. Model selection and threshold selection use validation data.
- Exported nominal-class ARFF files parse successfully and preserve split membership. RapidMiner classification XML is syntactically valid.
- Python compilation succeeded. The overview and model-performance figures were captured from the actual pages and visually inspected; see [chart gallery](diabetes_chart_gallery.png). The classification page was rerun after correcting the precision-recall plot's baseline representation.

## Measured held-out result

Validation selected the lab-plus-demographics random forest. On 1,020 held-out test respondents at its frozen 0.46 threshold: ROC AUC 0.8201, average precision 0.4879, precision 0.3283, recall 0.7844, and F1 0.4629. Confusion counts are TN 585, FP 268, FN 36, TP 131. These are reproducible sample classification results, not clinical validation. Detailed metrics and provenance are in `exports/diabetes/`.

## Validation limits

- RapidMiner and Weka were not executed. Their workflow templates and exchange formats are prepared; native import compatibility and external-tool metrics remain unverified.
- AppTest and rendered figures were checked. Full browser layout, responsiveness and browser interactions were not verified; browser automation was unavailable in this Windows environment.
- Tests emitted third-party Seaborn/Matplotlib deprecation warnings; these did not cause failures.
- No external or prospective model validation was performed. The target is self-reported doctor-told diabetes status; the model is not a diagnosis, future-risk forecast, or validated personal probability.
- No urine-strip hardware, RGB calibration, hospital integration or population prevalence claims are validated by this project.

Navigation update: removed the Project methodology entry and its page-test parameter; 10 pages remain. Python syntax and navigation references were checked after this change.
