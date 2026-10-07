# Urinalysis Lab — Fundamentals of Data Science

A complete local Streamlit dashboard using your NHANES workbook and all seven supplied FODS experiments. The graphs use **Matplotlib and Seaborn**, and modeling uses **scikit-learn**. Every Python module includes comments explaining its logical sections.

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
| Data explorer | Pandas/NumPy, numeric filters, column selection, dictionary, join, cleaning comparisons, CSV |
| Descriptive statistics | Mean, median, modes, variance, SD, range, IQR, grouped estimates and boxplots |
| Correlation | Manual Pearson r, three lab examples, trend lines, heatmap and pair counts |
| Regression & imputation | Simple/multiple linear regression, holdout scoring, baseline, residuals, eligible estimates |
| Scale & discretize | Min-max, z-score, decimal scaling, K-means, width/quantile bins, elbow curve |
| Visualization gallery | Line, bar, scatter, pie, box, histogram; violin, ECDF and sampled pair plot |
| RapidMiner & Weka | Downloadable train/test CSV + ARFF, Python benchmark and tool instructions |
| Use case & lab guide | Experiment coverage, data limitations, source links and viva walkthrough |

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
docs/                       Methodology, tool guide, presentation guide and test results
tests/                      Calculation and dashboard-interaction checks
.vscode/                    F5 launch and export-generation task
.streamlit/config.toml      Local theme and server settings
```

## RapidMiner and Weka

See `docs/RAPIDMINER_WEKA.md`. CSV/ARFF train/test files use the same split as Python. `tools/rapidminer_regression.rmp` provides an importable process; change the input paths if needed. `tools/run_weka.cmd` accepts the path to `weka.jar`.

The project does not bundle or install RapidMiner, Weka, Java, or their licenses. Python results are measured; native-tool execution status is recorded separately. A completed Python dashboard does not mean those desktop tools have been executed.

## Test and reproduce

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe prepare_exports.py
```

Model seed: 42. Default split: 80% training, 20% testing. Regression target: `LBXHCT`; default predictor: `LBXHGB`. The data loader reads Excel row 2 as column codes, avoiding the text-code row being counted as a participant.

## Scope

The PDF describes a ten-pad colorimetric reader. The workbook has clinical laboratory measurements, not RGB-to-concentration calibration pairs. This app is an educational analysis of those measurements, with the reader's future data requirements explained. It does not implement the hardware or provide clinical diagnoses. Summaries are unweighted sample descriptions; survey weights and design variables are absent.

Source details, caveats, and the experiment-by-experiment mapping are in `docs/METHODOLOGY.md` and the app's lab guide.
