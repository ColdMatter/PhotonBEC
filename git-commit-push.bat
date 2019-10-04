@echo off
set /p msg=Enter commit message :
echo %msg%
git commit -am "%msg%"
pause
git push https://github.com/ColdMatter/PhotonBEC.git
pause