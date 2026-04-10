@echo off
cd /d %~dp0
python src\pipeline.py >> logs\cron.log 2>&1
