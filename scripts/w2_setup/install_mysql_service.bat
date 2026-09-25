@echo off
rem ============================================================
rem Register and start MySQL80 Windows service.
rem MUST run elevated: right-click this file -> Run as administrator
rem Prereq: D:\mysql exists and D:\mysql\data already initialized
rem         (done by ZCode; if missing, see scripts\w2_setup\README.md)
rem ============================================================
net session >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Not running as administrator.
  echo         Right-click this file, choose "Run as administrator".
  pause
  exit /b 1
)

set MYSQL_HOME=D:\mysql

echo [1/3] Registering service MySQL80 ...
"%MYSQL_HOME%\bin\mysqld.exe" --install MySQL80 --defaults-file="%MYSQL_HOME%\my.ini"
if errorlevel 1 (
  echo [ERROR] Service registration failed. See message above.
  pause
  exit /b 1
)

echo [2/3] Starting service ...
net start MySQL80
if errorlevel 1 (
  echo [ERROR] Service start failed. Check: sc query MySQL80
  pause
  exit /b 1
)

echo [3/3] Adding D:\mysql\bin to machine PATH ...
powershell -NoProfile -Command "$p=[Environment]::GetEnvironmentVariable('Path','Machine'); if ($p -notlike '*D:\mysql\bin*') { [Environment]::SetEnvironmentVariable('Path', $p + ';D:\mysql\bin', 'Machine'); Write-Host 'PATH updated (new terminals only)' } else { Write-Host 'PATH already contains D:\mysql\bin' }"

echo.
echo ============================================================
echo [OK] MySQL80 installed and RUNNING.
echo.
echo Root password is EMPTY right now - set it immediately:
echo   1. Open a NEW terminal, type:  mysql -u root
echo      (no password yet, just press Enter if prompted)
echo   2. At the mysql^> prompt type:
echo        ALTER USER 'root'@'localhost' IDENTIFIED BY 'your-password';
echo      (pick your own password, remember it in your local notepad)
echo   3. Type:  exit
echo   4. Double-click:  scripts\w2_setup\yi_jian_chu_shi_hua or
echo      run one_click_init.py and enter that password
echo ============================================================
pause
