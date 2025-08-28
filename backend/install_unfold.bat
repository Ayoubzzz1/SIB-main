@echo off
echo ========================================
echo Installation de Django Unfold pour SIB
echo ========================================
echo.

echo 1. Installation de django-unfold...
pip install django-unfold

echo.
echo 2. Verification de l'installation...
python -c "import django_unfold; print('django-unfold installe avec succes!')"

echo.
echo 3. Nettoyage des anciens fichiers Jazzmin...
if exist "staticfiles\jazzmin" (
    echo Suppression du dossier jazzmin...
    rmdir /s /q "staticfiles\jazzmin"
)

echo.
echo 4. Collecte des fichiers statiques...
python manage.py collectstatic --noinput

echo.
echo 5. Redemarrage du serveur...
echo.
echo ========================================
echo Installation terminee!
echo ========================================
echo.
echo Pour demarrer le serveur:
echo python manage.py runserver
echo.
echo Ou utilisez: run_backend.bat
echo.
pause

