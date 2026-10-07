@echo off
rem Run a separate Weka Logistic comparator on the frozen test set.
if "%~1"=="" (
  echo Usage: run_weka_diabetes.cmd "C:\path\to\weka.jar"
  exit /b 1
)
cd /d "%~dp0.."
java -cp "%~1" weka.classifiers.functions.Logistic -t exports/diabetes/train.arff -T exports/diabetes/test.arff -c last > exports/diabetes/weka_results.tmp
if errorlevel 1 (
  echo Weka failed. Check Java, jar path, and the console error.
  exit /b 1
)
move /y exports\diabetes\weka_results.tmp exports\diabetes\weka_results.txt >nul
type exports\diabetes\weka_results.txt
