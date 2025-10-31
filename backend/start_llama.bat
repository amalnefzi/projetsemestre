@echo off
echo ========================================
echo 🤖 Démarrage du serveur Llama (Flask)
echo ========================================
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Changer vers le répertoire backend si nécessaire
cd /d "%~dp0"

echo ✅ Environnement virtuel activé
echo.
echo 🌐 Démarrage Flask Llama sur http://127.0.0.1:8000
echo 📝 Appuyez sur Ctrl+C pour arrêter
echo.

python llama_server.py

pause

