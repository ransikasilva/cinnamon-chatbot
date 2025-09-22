@echo off

FOR /F "tokens=*" %%A IN ('type "%cd%\conf\project_details.ini"') DO SET %%A
call conda activate %usecase_name%

call git %*
