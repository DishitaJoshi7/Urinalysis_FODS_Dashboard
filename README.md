# Urinalysis Lab — Fundamentals of Data Science

A local analytical dashboard for urine chemistry and complete blood count measurements from NHANES 2017–2018, developed for Fundamentals of Data Science. The graphs use **Matplotlib and Seaborn**, and modeling uses **scikit-learn**. Every Python module includes comments explaining its logical sections.

## Open in VS Code

1. Extract the ZIP, if using the archive.
2. Open `Urinalysis_FODS.code-workspace` in VS Code, or use **File → Open Folder** and choose this folder.
3. Install Python **3.12** and the VS Code Python extension if needed.
4. Open **Terminal → New Terminal** in the project folder and run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the localhost URL printed in the terminal (usually http://localhost:8501). Keep the terminal running; Ctrl+C stops the dashboard. These commands do not require PowerShell script activation or changes to execution policy.

Alternatively, double-click `setup_and_run.cmd`. After setup, select `.venv\Scripts\python.exe` using **Python: Select Interpreter** and press **F5** to launch with the included debug configuration. On macOS/Linux, use `python3.12 -m venv .venv` and `.venv/bin/python` in place of the Windows commands.

If `py` is unavailable but Python is installed, replace `py -3.12` with your Python 3.12 executable. If port 8501 is occupied, append `--server.port 8502` to the run command. Dependency installation needs internet; the dashboard then works locally without fetching data or fonts.

## What is included

| View | Features |
|---|---|
| Overview | Cohort counts, urine ACR distribution, missingness, source context |
| Data explorer | Numeric filters, column selection, data dictionary, source reconciliation, missing-value comparisons and CSV export |
| Descriptive statistics | Mean, median, modes, variance, SD, range, IQR, grouped estimates and boxplots |
| Correlation | Manual Pearson r, selected measurement relationships, trend lines, heatmap and pair counts |
| Regression & imputation | Simple/multiple linear regression, holdout scoring, baseline, residuals, eligible estimates |
| Normalization & clustering | Min-max, z-score, decimal scaling, K-means, width/quantile bins, elbow curve |
| Visualizations | Line, bar, scatter, pie, box, histogram; violin, ECDF and sampled pair plot |
| Data & model exports | Matched training/test CSV and ARFF files, Python benchmark and downloadable integration documentation |
| Project methodology | Study scope, analysis methods, data limitations and source links |

Use the sidebar to change the cohort. Page-specific exploration filters only affect that page. Charts offer PNG downloads, and analysis tables offer CSV exports. There are no invented demographics, patient timelines, diagnoses, or RGB readings.

## Project files

```text
app.py                      Application entry point and shared cohort selection
core.py                     Workbook loading, statistics, manual r, models, export logic
charts.py                   Matplotlib and Seaborn visualization functions
ui.py                       Cached loading and download/display helpers
app_pages/                  Nine commented dashboard page scripts
data/NHANES_2017_2018.xlsx   Unmodified copy of your workbook
prepare_exports.py          Regenerates tool data and benchmark
exports/                    CSV, ARFF, actual Python results and benchmark.json
tools/                      RapidMiner process and Weka command script
docs/                       Methodology, tool guide and test results
tests/                      Calculation and dashboard-interaction checks
.vscode/                    F5 launch and export-generation task
.streamlit/config.toml      Local theme and server settings
```

## RapidMiner and Weka

**Current status: integration files are prepared; neither external tool has been executed for this project.** All reported model metrics currently come from Python/scikit-learn.

| Tool | Prepared integration | Remaining validation |
|---|---|---|
| RapidMiner / Altair AI Studio | `tools/rapidminer_regression.rmp` and training/test CSV files | Import the process, set CSV paths, run it and record performance |
| Weka | Training/test ARFF files and `tools/run_weka.cmd` | Run LinearRegression with the supplied test set and record performance |

Both workflows predict **hematocrit (`LBXHCT`) from hemoglobin (`LBXHGB`)** using the same 80% training / 20% test records as the default Python model (seed 42). Respondent IDs are exported separately and must not be used as predictors.

The RapidMiner process follows **Read CSV → Set Role → Linear Regression → Apply Model → Performance (Regression)**. Weka uses **functions → LinearRegression** with a **Supplied test set**. Compare MAE and RMSE on the matching test records; Weka's correlation coefficient is not sklearn's R².

Detailed instructions: [RapidMiner and Weka integration](docs/RAPIDMINER_WEKA.md). The Weka command script requires the path to an installed `weka.jar`. This project does not bundle RapidMiner, Weka, Java or their licenses.

### Recorded Python reference results

Default full cohort; 5,797 training rows and 1,450 held-out rows:

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Linear regression | 0.7910 | 0.9972 | 0.9453 |
| Training-mean baseline | 3.3524 | 4.2660 | -0.0015 |

MAE and RMSE are in hematocrit percentage points. Source: `exports/python_metrics.csv`. Metrics in the app may change with cohort and model settings. External-tool results will be documented only after their workflows have actually been run.

## Test and reproduce

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe prepare_exports.py
```

Model seed: 42. Default split: 80% training, 20% testing. Regression target: `LBXHCT`; default predictor: `LBXHGB`. The data loader reads Excel row 2 as column codes, avoiding the text-code row being counted as a participant.

## Scope

The PDF describes a ten-pad colorimetric reader. The workbook has clinical laboratory measurements, not RGB-to-concentration calibration pairs. This app analyzes those laboratory measurements and documents the calibration data needed for the proposed reader. It does not implement the hardware or provide clinical diagnoses. Summaries are unweighted sample descriptions; survey weights and design variables are absent.

Source details, caveats, and the experiment-by-experiment mapping are in `docs/METHODOLOGY.md` and the app’s methodology page.

## Project status

Last updated: 7 October 2026.

- The dashboard presents analysis and results under professional section headings. Viva coaching and on-screen programming tutorials have been removed; explanatory code comments remain in the source.
- All nine analysis pages, chart downloads, data exports and model workflows are implemented.
- The initial automated suite passed 20 tests; a subsequent targeted run passed 10 tests. After the presentation cleanup, syntax checks passed for 11 application files, but the page-test rerun stalled and was stopped. The updated page rendering has not yet been fully reverified.
- RapidMiner and Weka execution and cross-tool metric comparison remain pending.
- This README tracks implemented functionality, measured results and outstanding validation as the project progresses.

## Subsequent runs and updates

Once dependencies are installed, start the complete dashboard from the project folder:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Refresh the browser after source changes, or stop with Ctrl+C and restart. To publish local changes to an already-connected GitHub repository, review and stage the files in VS Code Source Control, commit them, then sync/push. Editing the local project does not automatically update GitHub.
