@if "%ipAddress"=="169.254.99.1XX" (
  echo.
  echo Please configure the IP address of the Time Controller in the file ScpiClient.cmd
  echo.
  pause
  exit
)
@set controlPort=5555
@start /b DataLinkTarget.Service.exe > nul
@start /b ClientScpiServerCmdsCommunicatorConsole.exe -p -a tcp://%ipAddress%:%controlPort% -l tcp://*:6666 > nul
@ClientScpiServerCmdsCommunicatorConsole.exe -c -a tcp://localhost:6666
