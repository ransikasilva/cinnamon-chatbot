@echo off
FOR /F "tokens=*" %%A IN ('type "%cd%\conf\project_details.ini"') DO SET %%A
echo Use Case - %usecase_name%
goto main

:main
cls
echo Use Case - %usecase_name%
echo.
echo Select:
echo 1) Create Feature Branch
echo 2) Pre Commits Setup
echo 3) Set Up Databricks CLI Credentials
echo 4) Run Pre Commit on the recent changes
echo.
echo Import or Export Directory
echo 5) Import Databricks Notebooks Directory from Azure Databricks to local machine
echo 6) Export Databricks Notebooks Directory to Azure Databricks from local machine
echo.
echo Import or Export Single File
echo 7) Import Single Databricks Notebook Directory from Azure Databricks to local machine
echo 8) Export Single Databricks Notebooks Directory to Azure Databricks from local machine
echo.
echo 9) Commit and Push Your Work to Remote Feature Branch
echo 10) Syncing(git pull) remote development branch with local feature branch
echo 11) Sync Databricks Notebooks with DevOps
echo 12) Exit
echo.

set /p choice="Select options 1-11 : "
if %choice% == 1 goto label1
if %choice% == 2 goto label2
if %choice% == 3 goto label3
if %choice% == 4 goto label4
if %choice% == 5 goto label5
if %choice% == 6 goto label6
if %choice% == 7 goto label7
if %choice% == 8 goto label8
if %choice% == 9 goto label9
if %choice% == 10 goto label10
if %choice% == 11 goto label11
if %choice% == 12 exit

:label1
cls
echo =========================
echo Creatinig Feature Branch
echo =========================
git checkout development
git pull origin development
set /p f_branch="Feature Branch Name : "
git checkout -b %f_branch%
PAUSE
cls
goto main


:label2
cls
echo ====================
echo Pre Commits Setup
echo ====================
call conda activate base
call conda create -n %usecase_name% python=3.7
call conda activate %usecase_name%
call pip install -r test_requirements.txt
call pip install -r src/requirements.txt
pre-commit install
git config commit.template .git_commit_template
git config core.excludesFile .gitignore
git add .
pre-commit run --all-files
PAUSE
cls
goto main



:label3
cls
echo ===================================
echo Set Up Databricks CLI Credentials
echo ===================================
echo.
echo Installing databricks CLI
echo.
call conda activate base
REM call conda activate %usecase_name%
call pip install databricks-cli
echo.
echo Setting Up databricks credentials
echo.
call databricks configure --token
PAUSE
cls
goto main



:label4
cls
echo =====================================
echo Run Pre Commit on the recent changes
echo =====================================
call conda activate  %usecase_name%
git add .
call pre-commit run --all-files
PAUSE
cls
goto main

:label5
cls
echo =====================================
echo Import Databricks Notebooks to Local
echo =====================================
call conda activate  base
set /p r_folder="Databricks Folder Path :"
call databricks workspace export_dir "%r_folder%" "%cd%\" -o
call conda activate  %usecase_name%
echo.
git pull origin development
echo.
call black ./
PAUSE
cls
goto main

:label6
cls
echo ===========================================
echo Export Local Folder to Databricks Notebooks
echo ===========================================
call conda activate  base
set /p r_folder="Databricks Folder Path :"
call databricks workspace import_dir "%cd%\" "%r_folder%" -o
PAUSE
cls
goto main

:label7
cls
echo ==========================================
echo Import Single Databricks Notebook to Local
echo ==========================================
call conda activate  base
set /p r_file="Databricks File Path :"
set /p r_file_dest="Destination File Path including file name(within source folder after root ex: src/model/new_iteration):"
call databricks workspace export -o "%r_file%" "%cd%\%r_file_dest%.py"
for /f "delims== tokens=1,2" %%G in ("%cd%\conf\project_details.ini") do set %%G=%%H
call conda activate  %usecase_name%
echo.
git pull origin HEAD
echo.
call black ./
PAUSE
cls
goto main

:label8
cls
echo =========================================
echo Export .py File as a  Databricks Notebook
echo =========================================
call conda activate  base
set /p r_file_dest="Source File Path including file name(within source folder after root ex: src/model/new_iteration.py):"
set /p r_folder="Destination Databricks Folder Path including the file name:"
call databricks workspace import -l PYTHON -o "%cd%\%r_file_dest%" "%r_folder%"
PAUSE
cls
goto main


:label9
cls
echo =====================================
echo Commit Your Work to Feature Branch
echo =====================================
echo opening conda
echo.
call conda activate %usecase_name%
echo.
echo commiting changes to the repo
echo.
call git add .
git commit
echo.
git push origin HEAD
echo.
PAUSE
cls
goto main

:label10
cls
echo ===================================================================
echo Syncing(Pull) remote development branch with local feature branch
echo ===================================================================
git pull origin development
PAUSE
cls
goto main

:label11
cls
echo ==============================================
echo Sync Databricks Notebooks with DevOps Updates
echo ==============================================
call conda activate  base
set /p r_folder="Databricks Folder Path :"
call databricks workspace export_dir "%r_folder%" "%cd%\c" -o
call conda activate  %usecase_name%
echo.
git pull origin HEAD
echo.
call black ./
echo.
call databricks workspace import_dir "%cd%\" "%r_folder%" -o
PAUSE
cls
goto main
