@echo off
echo Initializing clm...

set MYSQL_USER=root
set MYSQL_PASS=123456
set DATABASE_NAME=clm
set SQL_FILE=E:\PycharmProject\FoodDelivery\mysql\SQLprogram.sql

echo Deleting and Rebuilding Database %DATABASE_NAME%...
echo DROP DATABASE IF EXISTS %DATABASE_NAME%; CREATE DATABASE %DATABASE_NAME% DEFAULT CHARSET utf8mb4; | mysql -u %MYSQL_USER% -p%MYSQL_PASS%

echo Importing SQL File：%SQL_FILE%
mysql -u %MYSQL_USER% -p%MYSQL_PASS% %DATABASE_NAME% < "%SQL_FILE%"

echo Successfully Init!
pause
