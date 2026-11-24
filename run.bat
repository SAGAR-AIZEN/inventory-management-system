@echo off
title Inventory Management System
echo ============================================================
echo   Starting CBSE Inventory Management System (MySQL / XAMPP)
echo ============================================================
python src\main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error code: %ERRORLEVEL%
    pause
)
