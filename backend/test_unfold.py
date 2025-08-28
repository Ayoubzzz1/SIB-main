#!/usr/bin/env python
"""
Test script pour vérifier l'installation de Django Unfold
"""

import os
import sys
import django

# Ajouter le chemin du projet Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sib.settings')

try:
    django.setup()
    print("✅ Django configuré avec succès")
except Exception as e:
    print(f"❌ Erreur lors de la configuration Django: {e}")
    sys.exit(1)

def test_unfold_import():
    """Teste l'import de django-unfold"""
    try:
        import django_unfold
        print("✅ django-unfold importé avec succès")
        print(f"   Version: {django_unfold.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Erreur lors de l'import de django-unfold: {e}")
        return False

def test_unfold_settings():
    """Teste la configuration Unfold dans settings.py"""
    try:
        from sib.settings import UNFOLD
        print("✅ Configuration UNFOLD trouvée dans settings.py")
        
        # Vérifier les clés importantes
        required_keys = ['SITE_TITLE', 'SITE_HEADER', 'SIDEBAR', 'COLORS']
        for key in required_keys:
            if key in UNFOLD:
                print(f"   ✅ {key}: {UNFOLD[key]}")
            else:
                print(f"   ❌ {key} manquant")
                return False
        
        return True
    except ImportError as e:
        print(f"❌ Erreur lors de l'import des settings: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des settings: {e}")
        return False

def test_dashboard_callback():
    """Teste le dashboard callback"""
    try:
        from sib.dashboard import dashboard_callback
        print("✅ Dashboard callback trouvé")
        return True
    except ImportError as e:
        print(f"❌ Erreur lors de l'import du dashboard callback: {e}")
        return False

def test_templates():
    """Teste l'existence des templates personnalisés"""
    template_files = [
        'templates/admin/index.html',
        'templates/admin/login.html'
    ]
    
    all_exist = True
    for template in template_files:
        if os.path.exists(template):
            print(f"✅ Template trouvé: {template}")
        else:
            print(f"❌ Template manquant: {template}")
            all_exist = False
    
    return all_exist

def test_static_files():
    """Teste l'existence des fichiers statiques personnalisés"""
    static_files = [
        'static/css/unfold_custom.css'
    ]
    
    all_exist = True
    for static_file in static_files:
        if os.path.exists(static_file):
            print(f"✅ Fichier statique trouvé: {static_file}")
        else:
            print(f"❌ Fichier statique manquant: {static_file}")
            all_exist = False
    
    return all_exist

def test_requirements():
    """Teste les requirements"""
    try:
        import pkg_resources
        django_unfold_dist = pkg_resources.get_distribution('django-unfold')
        print(f"✅ django-unfold installé: {django_unfold_dist.version}")
        return True
    except pkg_resources.DistributionNotFound:
        print("❌ django-unfold non installé")
        return False

def main():
    """Fonction principale de test"""
    print("=" * 50)
    print("🧪 TEST D'INSTALLATION DJANGO UNFOLD")
    print("=" * 50)
    print()
    
    tests = [
        ("Import django-unfold", test_unfold_import),
        ("Requirements", test_requirements),
        ("Configuration Unfold", test_unfold_settings),
        ("Dashboard callback", test_dashboard_callback),
        ("Templates personnalisés", test_templates),
        ("Fichiers statiques", test_static_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🔍 Test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Erreur lors du test: {e}")
            results.append((test_name, False))
        print()
    
    # Résumé
    print("=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print()
    print(f"Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Django Unfold est correctement configuré.")
        print("\n📝 Prochaines étapes:")
        print("1. Redémarrez le serveur Django")
        print("2. Accédez à /admin/ pour voir la nouvelle interface")
        print("3. Consultez UNFOLD_UI_GUIDE.md pour plus d'informations")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        print("\n🔧 Solutions possibles:")
        print("1. Exécutez: pip install django-unfold")
        print("2. Vérifiez que tous les fichiers sont présents")
        print("3. Consultez les logs d'erreur ci-dessus")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

