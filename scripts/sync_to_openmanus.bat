@echo off
rem Sync skeleton/student code from this repo (source of truth) into OpenManus runtime.
rem Run this after every edit, then run tests\test_tools.py
set REPO=%~dp0..
set OM=D:\projects\OpenManus

copy /Y "%REPO%\app\agent\ecommerce.py"    "%OM%\app\agent\ecommerce.py"    >nul
copy /Y "%REPO%\app\prompt\ecommerce.py"   "%OM%\app\prompt\ecommerce.py"   >nul
copy /Y "%REPO%\app\tool\sales_sql_query.py"  "%OM%\app\tool\sales_sql_query.py"  >nul
copy /Y "%REPO%\app\tool\sales_stats.py"      "%OM%\app\tool\sales_stats.py"      >nul
copy /Y "%REPO%\app\tool\plot_chart.py"       "%OM%\app\tool\plot_chart.py"       >nul
copy /Y "%REPO%\app\tool\report_generator.py" "%OM%\app\tool\report_generator.py" >nul

echo Sync done:
echo   app\agent\ecommerce.py   -^> %OM%\app\agent\
echo   app\prompt\ecommerce.py  -^> %OM%\app\prompt\
echo   app\tool\*.py (4 tools)  -^> %OM%\app\tool\
echo.
echo Next: run  python %REPO%\tests\test_tools.py
pause
