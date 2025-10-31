@echo off
echo ========================================
echo 🚀 Démarrage du serveur Django
echo ========================================
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Changer vers le répertoire backend si nécessaire
cd /d "%~dp0"

echo ✅ Environnement virtuel activé
echo.
echo 🌐 Démarrage Django sur http://127.0.0.1:8001
echo 📝 Appuyez sur Ctrl+C pour arrêter
echo.

python manage.py runserver 8001

pause

