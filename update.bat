@echo off

echo 提交当前改动...
git add .
git commit -m 'timely-commit'

echo 下载最新代码并覆盖本地...
git fetch --depth=1
git reset --hard origin/master
git pull

echo 代码更新完成！
pause