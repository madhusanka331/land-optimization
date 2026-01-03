@echo off
echo Setting up PostgreSQL database...
echo.

REM Set password for postgres user
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'admin';"

REM Create database
psql -U postgres -c "CREATE DATABASE land_optimization;"

REM Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE land_optimization TO postgres;"

echo.
echo Database setup complete!
echo Database: land_optimization
echo User: postgres
echo Password: admin
echo.
pause
