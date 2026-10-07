# Validation results

Validated on 7 October 2026 using Python 3.12 and the versions pinned in requirements.txt.

## Passed

- Full automated suite: **20 tests passed**. All nine dashboard pages completed without application exceptions.
- After the final Matplotlib orientation update: **10 targeted tests passed**, covering the core calculations and gallery rendering.
- Source merged table: **7,936 rows × 29 columns**, unique nonmissing SEQN identifiers.
- Reconstructed one-to-one urine/CBC join matches the supplied merged sheet, including missing values.
- Observed urine ACR: **7,632**. Observed hemoglobin: **7,247**. Complete merged rows: **7,073**.
- Manual correlation handles constant inputs, missing pairs, positive/negative relationships and agrees with an independent Pandas check.
- Scaling retains missing values and handles constants. Binning includes all observed values and the range endpoints.
- Train/test respondent IDs do not overlap. Eligible real imputation is tested on a controlled copy without altering the source.
- ARFF round-trip parsing preserves numeric schema and missing values. RapidMiner XML parses successfully.
- Cohort changes, simple/multiple regression switching, alternative discretization methods and ECDF selection are tested.
- The six Matplotlib chart outputs were rendered and visually inspected for readable labels, legends and nonclipped content.
- Streamlit server initialization succeeded, including loading the project theme.

## Actual default Python benchmark

Predictor: hemoglobin (LBXHGB). Target: hematocrit (LBXHCT). Seed 42; 5,797 training and 1,450 held-out rows.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Linear regression | 0.7910 | 0.9972 | 0.9453 |
| Training-mean baseline | 3.3524 | 4.2660 | -0.0015 |

MAE/RMSE are hematocrit percentage points. These are sample holdout results, not clinical validation. Of 689 missing hematocrit values, zero have observed hemoglobin, so the simple model cannot fill them from the supplied predictors.

## Limitations of validation

- In-app browser automation failed with a Windows sandbox initialization error. An alternative headless browser also exited during startup; full browser layout/responsiveness was not verified. Streamlit's AppTest ran successfully, and charts were independently rendered and inspected.
- Localhost access across tool sessions did not succeed, so a durable live preview is not included. Run the supplied launcher on your machine.
- The full suite emitted third-party Seaborn/Matplotlib deprecation warnings and a Windows temporary-folder cleanup warning after tests passed. The targeted rerun used a project-local temporary directory and completed cleanly.
- RapidMiner and Weka were not executed. XML syntax and ARFF format were checked; native-tool import/compatibility and performance require the installed desktop tools. The included workflow guide explicitly records this status.
- This project does not claim hardware, camera calibration, hospital integration, clinical safety, or regulatory validation.
