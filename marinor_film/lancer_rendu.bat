@echo off
chcp 65001 >nul
title Rendu du film - Marin'Or Ivoire
cd /d "%~dp0"
rem Rend les 2040 images du film dans rendu\images\ (Blender doit être fermé).
rem Relancer ce fichier reprend le rendu à la première image manquante.
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
if not exist "rendu\images" mkdir "rendu\images"
rem Une image interrompue laisse un fichier vide (0 octet) : on le supprime pour qu'elle soit refaite.
set /a VIDES=0
for %%F in ("rendu\images\marinor_*.png") do if %%~zF==0 (
  del "%%F"
  set /a VIDES+=1
)
set /a FAITES=0
for %%F in ("rendu\images\marinor_*.png") do set /a FAITES+=1
echo ============================================================
echo  Rendu du film Marin'Or Ivoire : 2040 images
echo  Images déjà rendues : %FAITES% / 2040
echo  Images interrompues supprimées (à refaire) : %VIDES%
echo.
echo  Laissez cette fenêtre ouverte (vous pouvez la réduire).
echo  Pour arrêter : Ctrl+C, puis O et Entrée.
echo  Pour reprendre : double-clic sur lancer_rendu.bat.
echo ============================================================
"%BLENDER%" -b "marinor_film.blend" -a
set /a FAITES=0
for %%F in ("rendu\images\marinor_*.png") do if not %%~zF==0 set /a FAITES+=1
echo.
echo ============================================================
echo  Images rendues : %FAITES% / 2040
if %FAITES% GEQ 2040 (echo  Rendu terminé : passez au montage du MP4 ^(GUIDE_RENDU.md, étape 7^).) else (echo  Rendu incomplet : double-clic sur lancer_rendu.bat pour continuer.)
echo ============================================================
pause
