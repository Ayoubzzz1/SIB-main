# 🏭 Guide de Gestion des Accès aux Entrepôts

## Vue d'ensemble
Ce système permet de contrôler l'accès des utilisateurs aux entrepôts et à leurs données (stock, mouvements, etc.).

## 🔐 Types d'Accès

### 1. Accès à Tous les Entrepôts
- L'utilisateur peut voir et gérer les données de **tous** les entrepôts
- Utilisez cette option pour les administrateurs ou superviseurs

### 2. Accès à des Entrepôts Spécifiques
- L'utilisateur ne peut voir que les données des entrepôts qui lui sont assignés
- Plus sécurisé et recommandé pour la plupart des utilisateurs

## 🛠️ Comment Configurer l'Accès

### Option 1: Via l'Interface Admin Django
1. Allez dans **Admin Django** → **Users**
2. Cliquez sur un utilisateur
3. Dans la section **Profil Utilisateur**:
   - **Accès à tous les entrepôts**: Cochez pour donner accès à tout
   - **Accès aux entrepôts**: Définissez les entrepôts spécifiques ci-dessous

### Option 2: Via la Ligne de Commande (Recommandé)

#### Voir tous les utilisateurs et leurs accès
```bash
python manage.py setup_warehouse_access --list-users
```

#### Donner accès à tous les entrepôts
```bash
python manage.py setup_warehouse_access --username nom_utilisateur --all-warehouses
```

#### Donner accès à des entrepôts spécifiques
```bash
python manage.py setup_warehouse_access --username nom_utilisateur --warehouses "Nom Entrepôt 1" "Nom Entrepôt 2"
```

## 📋 Exemples Pratiques

### Exemple 1: Donner accès à un magasinier à "Magasin 2"
```bash
python manage.py setup_warehouse_access --username magasinier1 --warehouses "Magasin 2"
```

### Exemple 2: Donner accès à un superviseur à tous les entrepôts
```bash
python manage.py setup_warehouse_access --username superviseur1 --all-warehouses
```

### Exemple 3: Donner accès à un commercial à plusieurs entrepôts
```bash
python manage.py setup_warehouse_access --username commercial1 --warehouses "Entrepôt Principal" "Magasin 2"
```

## 🔍 Vérifier que le Système Fonctionne

### Test de Filtrage des Données
```bash
python manage.py verify_warehouse_filtering
```

Ce test vérifie que:
- ✅ Les utilisateurs ne voient que les données de leurs entrepôts assignés
- ✅ Les administrateurs voient toutes les données
- ✅ Le filtrage fonctionne au niveau de la base de données

## 🚨 Points Importants

1. **Sécurité**: Les utilisateurs ne peuvent voir que les données de leurs entrepôts assignés
2. **Performance**: Le filtrage se fait au niveau de la base de données
3. **Flexibilité**: Vous pouvez facilement modifier les accès via l'admin ou la ligne de commande
4. **Audit**: Tous les changements d'accès sont tracés

## 🆘 Dépannage

### Problème: Un utilisateur ne voit aucune donnée
**Solution**: Vérifiez que l'utilisateur a des entrepôts assignés ou l'option "Accès à tous les entrepôts" activée

### Problème: Un utilisateur voit des données d'autres entrepôts
**Solution**: Vérifiez que l'option "Accès à tous les entrepôts" n'est pas activée par erreur

### Problème: Les changements d'accès ne prennent pas effet
**Solution**: Vérifiez que l'utilisateur se déconnecte et se reconnecte, ou redémarrez le serveur

## 📞 Support

Si vous rencontrez des problèmes:
1. Vérifiez les logs du serveur
2. Utilisez la commande de vérification
3. Testez avec un utilisateur de test
4. Contactez l'équipe technique
