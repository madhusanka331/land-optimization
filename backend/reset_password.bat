@echo off
echo ========================================
echo PostgreSQL Password Reset
echo ========================================
echo.

echo Step 1: Restarting PostgreSQL service...
net stop postgresql-x64-16
timeout /t 2 /nobreak >nul
net start postgresql-x64-16
timeout /t 3 /nobreak >nul
echo.

echo Step 2: Setting password to 'admin'...
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'admin';"
echo.

echo Step 3: Creating database 'land_optimization'...
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "CREATE DATABASE land_optimization;" 2>nul
if errorlevel 1 (
    echo Database already exists or created successfully.
) else (
    echo Database created successfully!
)
echo.

echo Step 4: Granting privileges...
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE land_optimization TO postgres;"
echo.

echo ========================================
echo Password reset complete!
echo ========================================
echo.
echo Database: land_optimization
echo User: postgres
echo Password: admin
echo.
echo Press any key to close...
pause >nul
