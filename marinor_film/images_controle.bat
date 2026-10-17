@echo off
chcp 65001 >nul
title Images de contrôle - Marin'Or Ivoire
cd /d "%~dp0"
rem Rend les images 450, 700 et 1050 du film dans rendu\controle\ (Blender doit être fermé).
set "BLENDER="
for %%B in ("C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" "C:\Program Files\Blender Foundation\Blender\blender.exe" "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe") do if not defined BLENDER if exist %%B set "BLENDER=%%~B"
if not defined BLENDER (
  echo Blender 5.1 introuvable. Clic droit sur ce fichier ^> Modifier ^(Bloc-notes^) : sur
  echo la ligne qui commence par « for », remplacez le premier chemin entre guillemets
  echo par celui de votre blender.exe ^(clic droit sur le raccourci Blender ^> Ouvrir
  echo l'emplacement du fichier^).
  pause
  exit /b 1
)
if not exist "marinor_film.blend" (
  echo marinor_film.blend introuvable : placez ce fichier .bat dans le Dossier de travail,
  echo à côté de marinor_film.blend.
  pause
  exit /b 1
)
if not exist "rendu\controle" mkdir "rendu\controle"
del /q "rendu\controle\controle_*.png" 2>nul
echo ============================================================
echo  Images de contrôle 450, 700 et 1050 (environ 3 à 5 minutes)
echo  Le temps de chaque image est sur la ligne « Saved: ... Time: »
echo ============================================================
"%BLENDER%" -b "marinor_film.blend" -o "//rendu/controle/controle_####" -F PNG -x 1 -f 450,700,1050
echo.
echo Terminé : les images sont dans rendu\controle\
start "" "rendu\controle"
pause
