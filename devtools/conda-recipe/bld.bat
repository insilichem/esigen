if not exist "%PREFIX%\Menu" mkdir "%PREFIX%\Menu"
copy "%RECIPE_DIR%\menu-windows.json" "%PREFIX%\Menu"
copy "%RECIPE_DIR%\app.ico" "%PREFIX%\Menu"

"%SCRIPTS%\pip" install apscheduler cclib flask flask-sslify markdown gunicorn requests
if %errorlevel% neq 0 exit /b %errorlevel%
"%PYTHON%" setup.py install
