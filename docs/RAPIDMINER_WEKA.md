## Common dataset and evaluation

`exports/train.csv` / `train.arff` contain training records; the matching test files contain the exact Python holdout. Both have two numeric columns: `LBXHGB` predictor and `LBXHCT` target. IDs are stored separately for auditing and must not be joined back as predictors. The target is the last attribute. Seed 42 and an 80/20 split are fixed in `prepare_exports.py`.

`exports/python_metrics.csv` records the actual Python benchmark. Compare MAE and RMSE across tools. Their default feature-selection and regularization options can cause small differences; configure ordinary least squares where possible. Weka's reported correlation coefficient is not the same statistic as sklearn's coefficient of determination (R²).

## RapidMiner / Altair AI Studio

1. Install/open your course's RapidMiner/AI Studio version.
2. Import `tools/rapidminer_regression.rmp` using **File → Import Process**, or paste its XML into the XML view.
3. In the two **Read CSV** operators, set absolute paths to `exports/train.csv` and `exports/test.csv`. Relative paths in the template assume the project folder is the working directory. The first row is a header, separator is comma, decimal separator is a period, both attributes numeric.
4. Each input feeds **Set Role**, with attribute `LBXHCT` and role `label`.
5. Training data feeds **Linear Regression**. Set feature selection to none and ridge to zero; names/options can vary by installed version.
6. Connect the model to **Apply Model** and test data to its unlabeled input. Its labeled output goes to **Performance (Regression)**; enable root mean squared error and absolute error.
7. Run, record the performance output and save your process/screenshots for the course submission.

If your version cannot import the template, recreate that operator chain in the visual editor. The supplied process is a starting workflow whose native execution has not been verified here. For a new split instead of the supplied pair, **Split Validation** separates training and testing subprocesses; use 80% training, shuffled sampling and a documented seed. Tool RNGs can differ, so use the supplied pair for exact row comparability. [Official Split Validation documentation](https://support.rapidminer.com/latest/studio/operators/validation/split_validation.html)

For Experiment 6, import `cbc_exploration.csv`, select one measurement, handle its missing values, and try **Normalize**, **Discretize by Binning**, and **k-Means**. Fit transforms inside the training branch if evaluating a predictive model. Exploratory whole-cohort transformations are a separate exercise.

## Weka Explorer

1. Launch Explorer and open `exports/train.arff` in **Preprocess**.
2. Confirm both attributes are numeric. Set the class/target to `LBXHCT`.
3. In **Classify**, select `functions → LinearRegression`.
4. Configure attribute selection as **No attribute selection**, ridge `0`, and keep the single predictor. In the CLI these are `-S 1 -R 0`.
5. Select **Supplied test set**, choose `exports/test.arff`, and press **Start**.
6. Record MAE and RMSE alongside the Python results. Save result text/model from the result list if your submission needs it.

The ARFF files have identical attribute schemas, and the missing-value encoding is `?`. The numeric target means this is regression, even though Weka's tab is called Classify. [Official Weka Explorer guide](https://weka.sourceforge.net/manuals/ExplorerGuide.pdf)

Command-line equivalent (requires Java and your installed `weka.jar`):

```powershell
java -cp "C:\path\to\weka.jar" weka.classifiers.functions.LinearRegression -t exports/train.arff -T exports/test.arff -c last -S 1 -R 0
```

Or run `tools\run_weka.cmd "C:\path\to\weka.jar"`. It writes `exports/weka_results.txt` only after successful execution.

For exploration, open `cbc_exploration.arff`, select an attribute and use **Visualize All** for the scatter matrix. In Preprocess, filters under **unsupervised → attribute** include Normalize, Standardize and Discretize. Weka Standardize uses its own convention; this app's teaching z-score explicitly uses sample SD. In Cluster, apply SimpleKMeans with k=3 and seed 42 to a single selected measurement after handling missingness. Treat cluster labels as arbitrary and compare sorted centroids.

## Execution status

Python calculations, exports and dashboard pages were tested in this workspace; see `VALIDATION.md`. RapidMiner and Weka desktop sessions were not run. Do not report external-tool performance until you execute the provided workflows. No installation or licensing is implied by this project bundle.
