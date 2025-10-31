@echo off
echo ========================================
echo 🚀 Démarrage de tous les serveurs
echo ========================================
echo.
echo Cette fenêtre va démarrer le serveur Django (port 8001)
echo Ouvrez une NOUVELLE fenêtre de terminal et exécutez:
echo    start_llama.bat
echo.
echo OU utilisez deux terminaux séparés:
echo   Terminal 1: start_llama.bat
echo   Terminal 2: start_django.bat
echo.
echo ========================================
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Changer vers le répertoire backend si nécessaire
cd /d "%~dp0"

echo ✅ Environnement virtuel activé
echo.
echo 🌐 Démarrage Django sur http://127.0.0.1:8001
echo.
echo ⚠️  ATTENTION: Vous devez aussi démarrer le serveur Llama!
echo    Exécutez dans un autre terminal: start_llama.bat
echo.

python manage.py runserver 8001

pause

