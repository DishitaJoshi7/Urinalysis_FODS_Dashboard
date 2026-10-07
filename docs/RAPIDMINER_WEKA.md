# Diabetes classification in RapidMiner and Weka

## Shared evaluation files

Use exports/diabetes/, not the older root-level CBC regression files. The train/validation/test files have the same rows as Python's stratified 60/20/20 split. IDs are separate. The class is DIABETES_REPORTED with nominal values no and yes (yes is positive). Tool-ready data uses medians fitted on train only; raw files retain missing values. Both classes remain in every split.

These exports enable additional tool comparisons; they do not reproduce Python's missing-indicator features, class weights or exact model implementation. Native-tool performance is currently unmeasured. Do not present Python results as Weka/RapidMiner results.

## RapidMiner / Altair AI Studio

1. Import tools/rapidminer_diabetes.rmp. In both Read CSV operators, set absolute paths to exports/diabetes/train.csv and test.csv.
2. Confirm numerical predictors and a nominal DIABETES_REPORTED column. Both Set Role operators assign it the label role.
3. The template fits a Decision Tree on training rows, applies it to the test rows, and measures binominal classification performance. This is a separate comparator, not a replica of the Python forest.
4. Check that the positive class is yes. Record confusion counts, precision, recall, F1 and ROC AUC where supported by your version.
5. If tuning any parameters or threshold, apply the candidate model to validation.csv first. Freeze settings, then evaluate test.csv once. Do not choose settings based on test performance.
6. Save measured outputs/screenshots and your final process. If template compatibility differs, recreate Read CSV → Set Role → Decision Tree → Apply Model → Performance (Binominal Classification) in the visual editor.

[Official validation documentation](https://support.rapidminer.com/latest/studio/operators/validation/split_validation.html)

## Weka Explorer

1. Open exports/diabetes/train.arff in Preprocess. Set the last attribute DIABETES_REPORTED as class; it must display nominal no/yes, not numeric.
2. In Classify choose functions → Logistic. The supplied files already contain training-median imputation, so do not fit preprocessing on the combined dataset.
3. Choose Supplied test set. Use validation.arff for model development and test.arff only after freezing the settings.
4. Run and save the classifier output, confusion matrix and per-class metrics for yes. Weka's default decision rule may differ from the Python validation-selected threshold; state that in comparisons.
5. A command-line evaluation is provided in tools/run_weka_diabetes.cmd; pass the installed weka.jar path. It evaluates a default Logistic comparator and saves actual output only after success.

[Official Weka Explorer guide](https://weka.sourceforge.net/manuals/ExplorerGuide.pdf)

## What remains to complete

Both native tools must be run locally; neither was executed by this project build. Their installations/licenses are not bundled. Add measured native-tool results to the README only after execution. The older tools/rapidminer_regression.rmp and tools/run_weka.cmd remain for the supplementary hematocrit regression and are not diabetes classifiers.
