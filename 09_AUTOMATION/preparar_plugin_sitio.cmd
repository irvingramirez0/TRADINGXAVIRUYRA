@echo off
REM Prepara el enlace del plugin de componentes del sitio.
REM
REM Quartz instala un plugin de carpeta enlazándolo en `.quartz/plugins/<nombre>`
REM y para los `peerDependencies` enlaza también la copia de `preact` del host.
REM En Windows `fs.symlinkSync` falla con EPERM sin privilegios ni modo
REM desarrollador, así que se crean junctions (mklink /J), que no los necesitan.
REM
REM Uso:  09_AUTOMATION\preparar_plugin_sitio.cmd
REM       (se ejecuta antes de `node ./quartz/bootstrap-cli.mjs build`)

setlocal
set BASE=%~dp0..
set QZ=%BASE%\13_SITE\quartz

if not exist "%QZ%" (
  echo ERROR: no existe %QZ%
  exit /b 1
)

if not exist "%QZ%\.quartz\plugins" mkdir "%QZ%\.quartz\plugins"

for %%P in (ficha-fuente panel-avance anotaciones) do (
  if exist "%QZ%\.quartz\plugins\%%P" rmdir "%QZ%\.quartz\plugins\%%P" >nul 2>&1
  mklink /J "%QZ%\.quartz\plugins\%%P" "%QZ%\quartz-plugins\%%P" >nul
  if not exist "%QZ%\quartz-plugins\%%P\node_modules" mkdir "%QZ%\quartz-plugins\%%P\node_modules"
  if exist "%QZ%\quartz-plugins\%%P\node_modules\preact" rmdir "%QZ%\quartz-plugins\%%P\node_modules\preact" >nul 2>&1
  mklink /J "%QZ%\quartz-plugins\%%P\node_modules\preact" "%QZ%\node_modules\preact" >nul
  echo   %%P listo
)

echo Enlaces preparados. Ya se puede compilar.
endlocal
