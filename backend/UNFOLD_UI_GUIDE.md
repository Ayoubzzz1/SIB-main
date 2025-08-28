# 🎨 SIB Admin avec Django Unfold UI

## Vue d'ensemble

SIB utilise maintenant **Django Unfold** comme interface d'administration moderne et attrayante, remplaçant l'ancien Jazzmin. Unfold offre une expérience utilisateur exceptionnelle avec un design moderne, des animations fluides et une interface responsive.

## ✨ Caractéristiques principales

### 🎯 Interface moderne
- **Design épuré** avec des couleurs harmonieuses
- **Animations fluides** et transitions élégantes
- **Typographie optimisée** avec la police Inter
- **Mode sombre** automatique selon les préférences système

### 🚀 Expérience utilisateur améliorée
- **Navigation intuitive** avec icônes Heroicons
- **Recherche globale** dans toute l'interface
- **Tableau de bord personnalisé** avec statistiques en temps réel
- **Responsive design** pour tous les appareils

### 🎨 Personnalisation avancée
- **Thème personnalisé** avec palette de couleurs SIB
- **Icônes contextuelles** pour chaque module
- **Navigation organisée** par catégories logiques
- **CSS personnalisé** pour une identité visuelle unique

## 🛠️ Installation

### 1. Prérequis
```bash
# Assurez-vous d'être dans le dossier backend/sib
cd backend/sib

# Vérifiez que Python et pip sont installés
python --version
pip --version
```

### 2. Installation automatique (recommandé)
```bash
# Exécutez le script d'installation
install_unfold.bat
```

### 3. Installation manuelle
```bash
# Installer django-unfold
pip install django-unfold

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Démarrer le serveur
python manage.py runserver
```

## 🎨 Configuration

### Fichier de configuration principal
Le fichier `sib/settings.py` contient toute la configuration Unfold :

```python
UNFOLD = {
    "SITE_TITLE": "SIB Admin",
    "SITE_HEADER": "Administration SIB",
    "SITE_SYMBOL": "🏢",
    "COLORS": {
        "primary": { ... },
        "gray": { ... }
    },
    "SIDEBAR": {
        "navigation": [ ... ]
    }
}
```

### Personnalisation des couleurs
```python
"COLORS": {
    "primary": {
        "500": "168 85 247",  # Violet principal
        "600": "147 51 234",  # Violet foncé
        "700": "126 34 206",  # Violet très foncé
    }
}
```

### Navigation personnalisée
```python
"SIDEBAR": {
    "navigation": [
        {
            "title": "Inventaire",
            "app": "inventory_app",
            "icon": "heroicons:cube",
            "models": [
                {"model": "inventory_app.matierepremiere", "icon": "heroicons:cube-transparent"},
                {"model": "inventory_app.stock", "icon": "heroicons:building-storefront"},
            ]
        }
    ]
}
```

## 🎭 Templates personnalisés

### Dashboard principal
- **Fichier**: `templates/admin/index.html`
- **Fonctionnalités**: 
  - Accueil personnalisé avec logo SIB
  - Actions rapides pour les modules principaux
  - Statistiques en temps réel
  - Navigation intuitive par application

### Page de connexion
- **Fichier**: `templates/admin/login.html`
- **Fonctionnalités**:
  - Design moderne avec dégradés
  - Animations d'entrée
  - Validation en temps réel
  - Responsive design

## 🎨 CSS personnalisé

### Fichier principal
- **Fichier**: `static/css/unfold_custom.css`
- **Fonctionnalités**:
  - Variables CSS pour la cohérence des couleurs
  - Animations et transitions
  - Support du mode sombre
  - Design responsive

### Classes utilitaires
```css
.fade-in { animation: fadeIn 0.5s ease-in; }
.slide-up { animation: slideUp 0.5s ease-out; }
.loading { /* État de chargement */ }
```

## 🔧 Fonctionnalités avancées

### Dashboard callback
```python
# sib/dashboard.py
def dashboard_callback(request, context):
    # Statistiques en temps réel
    context.update({
        'total_stock_items': Stock.objects.count(),
        'recent_orders': Commande.objects.filter(...).count(),
        'active_productions': Production.objects.filter(...).count(),
    })
    return context
```

### Icônes Heroicons
Unfold utilise les icônes Heroicons pour une cohérence visuelle :
- `heroicons:users` - Utilisateurs
- `heroicons:cube` - Inventaire
- `heroicons:shopping-cart` - Ventes
- `heroicons:building-office` - Production

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Adaptations
- Sidebar collapsible sur mobile
- Grilles adaptatives pour les statistiques
- Navigation tactile optimisée
- Typographie responsive

## 🌙 Mode sombre

### Activation automatique
```python
"DARK_MODE": {
    "enabled": True,
    "default": False,  # Suit les préférences système
}
```

### Variables CSS
```css
@media (prefers-color-scheme: dark) {
    :root {
        --gray-50: #111827;
        --gray-100: #1f2937;
        /* ... autres couleurs sombres */
    }
}
```

## 🚀 Performance

### Optimisations
- **CSS optimisé** avec variables CSS
- **Animations hardware-accelerated**
- **Lazy loading** des composants
- **Cache des fichiers statiques**

### Monitoring
- Temps de chargement des pages
- Performance des animations
- Utilisation mémoire
- Temps de réponse des requêtes

## 🔍 Dépannage

### Problèmes courants

#### 1. Styles non chargés
```bash
# Vérifiez que les fichiers statiques sont collectés
python manage.py collectstatic --noinput

# Vérifiez le chemin dans settings.py
"STYLES": ["/static/css/unfold_custom.css"]
```

#### 2. Erreurs de template
```bash
# Vérifiez que les templates sont dans le bon dossier
templates/admin/index.html
templates/admin/login.html
```

#### 3. Problèmes de migration
```bash
# Redémarrez le serveur après les changements
python manage.py runserver
```

## 📚 Ressources

### Documentation officielle
- [Django Unfold Documentation](https://unfoldadmin.com/)
- [Heroicons](https://heroicons.com/)
- [Inter Font](https://rsms.me/inter/)

### Support
- Issues GitHub du projet SIB
- Documentation Django officielle
- Communauté Django Unfold

## 🎯 Prochaines étapes

### Améliorations futures
- [ ] Widgets de tableau de bord personnalisés
- [ ] Graphiques et visualisations
- [ ] Notifications en temps réel
- [ ] Intégration avec l'API REST
- [ ] Thèmes supplémentaires

### Personnalisation
- [ ] Logo et branding personnalisés
- [ ] Couleurs d'entreprise
- [ ] Workflows métier spécifiques
- [ ] Intégrations tierces

---

**Note**: Cette interface remplace complètement Jazzmin. Toutes les fonctionnalités existantes sont préservées avec une expérience utilisateur considérablement améliorée.

