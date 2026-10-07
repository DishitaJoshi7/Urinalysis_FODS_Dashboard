@echo off
rem Pass the actual installed weka.jar path as the first argument.
if "%~1"=="" (
  echo Usage: run_weka.cmd "C:\path\to\weka.jar"
  exit /b 1
)
cd /d "%~dp0.."
java -cp "%~1" weka.classifiers.functions.LinearRegression -t exports/train.arff -T exports/test.arff -c last -S 1 -R 0 > exports/weka_results.tmp
if errorlevel 1 (
  echo Weka failed. Check Java, the jar path, and the console error.
  exit /b 1
)
move /y exports\weka_results.tmp exports\weka_results.txt >nul
type exports\weka_results.txt
