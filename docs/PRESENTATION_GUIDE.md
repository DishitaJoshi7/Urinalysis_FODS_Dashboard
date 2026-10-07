1. **Problem (30 seconds):** The use case aims to reduce subjective reading of urine-strip colors. Explain why paired color and reference measurements would be necessary for calibration.
2. **Dataset (45 seconds):** Show the 7,936 matched NHANES records, variable dictionary and missingness. Explain the two-row Excel header and SEQN join.
3. **Exploration (45 seconds):** Filter a measurement; compare retaining, deleting and mean/median filling. Explain why missing is not zero.
4. **Statistics (45 seconds):** Interpret mean versus median for skewed ACR, an IQR boxplot, sample SD, and grouped approximations.
5. **Correlation (45 seconds):** Show the manual Pearson formula and positive, negative and weak examples. Explain pairwise deletion and correlation versus causation.
6. **Regression (60 seconds):** Compare simple and multiple regression and explain the untouched holdout, mean baseline, RMSE and residual plot. Show why the real missing rows cannot be imputed without observed predictors.
7. **Transformations (45 seconds):** Contrast min-max, z-score and decimal scaling. Change k and distinguish statistical clusters from clinical categories.
8. **Plots (45 seconds):** Identify line, bar, scatter, pie, box and histogram. The line uses percentiles because there are no repeated timestamps.
9. **Tools (45 seconds):** Load the supplied CSV/ARFF files in RapidMiner/Weka. Use the fixed test set to compare MAE/RMSE. Report only results you actually ran.
10. **Conclusion (30 seconds):** State what this analysis supports and which RGB/strip calibration data are needed next.

### Common viva questions

- **Why two regression models?** To compare one predictor with multiple predictors while keeping evaluation separate from training.
- **Why no train accuracy alone?** A model can fit training observations while failing on new data.
- **Why does z-scoring not produce normal data?** It changes location and scale, not the distribution's shape.
- **Why omit SEQN?** It is an identifier with no intended predictive meaning.
- **Why exclude duplicate-unit columns?** They encode the same information and can inflate apparent relationships.
- **Why can imputation reduce uncertainty incorrectly?** A predicted value is treated as exact unless its uncertainty and provenance are retained.
- **Why not predict the ten strip analytes?** There are no pad RGB features or matched ten-analyte calibration targets in this workbook.
- **Why not show nationwide prevalence?** The supplied workbook lacks the survey weighting and design fields required for that analysis.
