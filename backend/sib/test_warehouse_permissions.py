#!/usr/bin/env python
"""
Test script to demonstrate warehouse permissions functionality
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sib.settings')
django.setup()

from django.contrib.auth.models import User
from users_app.models import Utilisateur, UtilisateurEntrepot
from warehouse.models import Entrepot
from inventory_app.models import Stock, MatierePremiere

def create_test_data():
    """Create test data for warehouse permissions"""
    print("Creating test data...")
    
    # Create warehouses
    entrepot1, created = Entrepot.objects.get_or_create(
        nom="Magasin 1",
        defaults={'adresse': "123 Rue de la Logistique", 'description': "Entrepôt principal"}
    )
    entrepot2, created = Entrepot.objects.get_or_create(
        nom="Magasin 2", 
        defaults={'adresse': "456 Avenue du Stockage", 'description': "Entrepôt secondaire"}
    )
    
    print(f"Created warehouses: {entrepot1.nom}, {entrepot2.nom}")
    
    # Create raw material
    matiere, created = MatierePremiere.objects.get_or_create(
        nom="Acier",
        defaults={'code_reference': "AC001", 'unite': "kg", 'description': "Acier de construction"}
    )
    
    # Create stock in both warehouses
    stock1, created = Stock.objects.get_or_create(
        content_type_id=matiere.content_type_id,
        id_article=matiere.id,
        entrepot=entrepot1,
        defaults={'quantite': 1000, 'type_article': 'matiere'}
    )
    
    stock2, created = Stock.objects.get_or_create(
        content_type_id=matiere.content_type_id,
        id_article=matiere.id,
        entrepot=entrepot2,
        defaults={'quantite': 500, 'type_article': 'matiere'}
    )
    
    print(f"Created stock: {stock1.quantite}kg in {entrepot1.nom}, {stock2.quantite}kg in {entrepot2.nom}")
    
    return entrepot1, entrepot2, matiere

def create_test_users():
    """Create test users with different warehouse permissions"""
    print("\nCreating test users...")
    
    # Create admin user (access to all warehouses)
    admin_user, created = User.objects.get_or_create(
        username='admin_warehouse',
        defaults={'email': 'admin@warehouse.com', 'first_name': 'Admin', 'last_name': 'Warehouse'}
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
    admin_utilisateur, created = Utilisateur.objects.get_or_create(
        user=admin_user,
        defaults={'nom': 'Admin Warehouse', 'role': 'admin', 'acces_tous_entrepots': True}
    )
    print(f"Created admin user: {admin_utilisateur.nom} (access to all warehouses)")
    
    # Create magasinier user with access to only Magasin 1 (full permissions)
    magasinier_user, created = User.objects.get_or_create(
        username='magasinier1',
        defaults={'email': 'magasinier1@warehouse.com', 'first_name': 'Magasinier', 'last_name': 'Un'}
    )
    if created:
        magasinier_user.set_password('magasinier123')
        magasinier_user.save()
    
    magasinier_utilisateur, created = Utilisateur.objects.get_or_create(
        user=magasinier_user,
        defaults={'nom': 'Magasinier Un', 'role': 'magasin', 'acces_tous_entrepots': False}
    )
    
    # Give full access to Magasin 1
    entrepot1 = Entrepot.objects.get(nom="Magasin 1")
    UtilisateurEntrepot.objects.get_or_create(
        utilisateur=magasinier_utilisateur,
        entrepot=entrepot1,
        defaults={
            'peut_lire': True,
            'peut_modifier': True,
            'peut_supprimer': True
        }
    )
    
    print(f"Created magasinier user: {magasinier_utilisateur.nom} (full access to {entrepot1.nom} only)")
    
    # Create commercial user with read-only access to both warehouses
    commercial_user, created = User.objects.get_or_create(
        username='commercial1',
        defaults={'email': 'commercial1@warehouse.com', 'first_name': 'Commercial', 'last_name': 'Un'}
    )
    if created:
        commercial_user.set_password('commercial123')
        commercial_user.save()
    
    commercial_utilisateur, created = Utilisateur.objects.get_or_create(
        user=commercial_user,
        defaults={'nom': 'Commercial Un', 'role': 'commercial', 'acces_tous_entrepots': False}
    )
    
    # Give read-only access to both warehouses
    entrepot1 = Entrepot.objects.get(nom="Magasin 1")
    entrepot2 = Entrepot.objects.get(nom="Magasin 2")
    
    UtilisateurEntrepot.objects.get_or_create(
        utilisateur=commercial_utilisateur,
        entrepot=entrepot1,
        defaults={
            'peut_lire': True,
            'peut_modifier': False,
            'peut_supprimer': False
        }
    )
    
    UtilisateurEntrepot.objects.get_or_create(
        utilisateur=commercial_utilisateur,
        entrepot=entrepot2,
        defaults={
            'peut_lire': True,
            'peut_modifier': False,
            'peut_supprimer': False
        }
    )
    
    print(f"Created commercial user: {commercial_utilisateur.nom} (read-only access to both warehouses)")
    
    # Create production user with read and modify access to Magasin 2 only
    production_user, created = User.objects.get_or_create(
        username='production1',
        defaults={'email': 'production1@warehouse.com', 'first_name': 'Production', 'last_name': 'Un'}
    )
    if created:
        production_user.set_password('production123')
        production_user.save()
    
    production_utilisateur, created = Utilisateur.objects.get_or_create(
        user=production_user,
        defaults={'nom': 'Production Un', 'role': 'production', 'acces_tous_entrepots': False}
    )
    
    # Give read and modify access to Magasin 2 only
    UtilisateurEntrepot.objects.get_or_create(
        utilisateur=production_utilisateur,
        entrepot=entrepot2,
        defaults={
            'peut_lire': True,
            'peut_modifier': True,
            'peut_supprimer': False
        }
    )
    
    print(f"Created production user: {production_utilisateur.nom} (read and modify access to {entrepot2.nom} only)")
    
    return admin_utilisateur, magasinier_utilisateur, commercial_utilisateur, production_utilisateur

def test_warehouse_access():
    """Test warehouse access for different users"""
    print("\nTesting warehouse access...")
    
    entrepot1 = Entrepot.objects.get(nom="Magasin 1")
    entrepot2 = Entrepot.objects.get(nom="Magasin 2")
    
    # Test admin user
    admin_utilisateur = Utilisateur.objects.get(user__username='admin_warehouse')
    print(f"\nAdmin user ({admin_utilisateur.nom}):")
    print(f"  Access to {entrepot1.nom}: {admin_utilisateur.has_warehouse_access(entrepot1)}")
    print(f"  Access to {entrepot2.nom}: {admin_utilisateur.has_warehouse_access(entrepot2)}")
    print(f"  Accessible warehouses: {list(admin_utilisateur.get_accessible_warehouses().values_list('nom', flat=True))}")
    
    # Test magasinier user
    magasinier_utilisateur = Utilisateur.objects.get(user__username='magasinier1')
    print(f"\nMagasinier user ({magasinier_utilisateur.nom}):")
    print(f"  Access to {entrepot1.nom}: {magasinier_utilisateur.has_warehouse_access(entrepot1)}")
    print(f"  Access to {entrepot2.nom}: {magasinier_utilisateur.has_warehouse_access(entrepot2)}")
    print(f"  Read access to {entrepot1.nom}: {magasinier_utilisateur.has_warehouse_read_access(entrepot1)}")
    print(f"  Write access to {entrepot1.nom}: {magasinier_utilisateur.has_warehouse_write_access(entrepot1)}")
    print(f"  Delete access to {entrepot1.nom}: {magasinier_utilisateur.has_warehouse_delete_access(entrepot1)}")
    print(f"  Accessible warehouses: {list(magasinier_utilisateur.get_accessible_warehouses().values_list('nom', flat=True))}")
    
    # Test commercial user
    commercial_utilisateur = Utilisateur.objects.get(user__username='commercial1')
    print(f"\nCommercial user ({commercial_utilisateur.nom}):")
    print(f"  Access to {entrepot1.nom}: {commercial_utilisateur.has_warehouse_access(entrepot1)}")
    print(f"  Access to {entrepot2.nom}: {commercial_utilisateur.has_warehouse_access(entrepot2)}")
    print(f"  Read access to {entrepot1.nom}: {commercial_utilisateur.has_warehouse_read_access(entrepot1)}")
    print(f"  Write access to {entrepot1.nom}: {commercial_utilisateur.has_warehouse_write_access(entrepot1)}")
    print(f"  Read access to {entrepot2.nom}: {commercial_utilisateur.has_warehouse_read_access(entrepot2)}")
    print(f"  Write access to {entrepot2.nom}: {commercial_utilisateur.has_warehouse_write_access(entrepot2)}")
    print(f"  Accessible warehouses: {list(commercial_utilisateur.get_accessible_warehouses().values_list('nom', flat=True))}")
    
    # Test production user
    production_utilisateur = Utilisateur.objects.get(user__username='production1')
    print(f"\nProduction user ({production_utilisateur.nom}):")
    print(f"  Access to {entrepot1.nom}: {production_utilisateur.has_warehouse_access(entrepot1)}")
    print(f"  Access to {entrepot2.nom}: {production_utilisateur.has_warehouse_access(entrepot2)}")
    print(f"  Read access to {entrepot2.nom}: {production_utilisateur.has_warehouse_read_access(entrepot2)}")
    print(f"  Write access to {entrepot2.nom}: {production_utilisateur.has_warehouse_write_access(entrepot2)}")
    print(f"  Delete access to {entrepot2.nom}: {production_utilisateur.has_warehouse_delete_access(entrepot2)}")
    print(f"  Accessible warehouses: {list(production_utilisateur.get_accessible_warehouses().values_list('nom', flat=True))}")

def test_stock_filtering():
    """Test stock filtering based on warehouse permissions"""
    print("\nTesting stock filtering...")
    
    # Test admin user can see all stock
    admin_utilisateur = Utilisateur.objects.get(user__username='admin_warehouse')
    admin_stock = Stock.objects.filter(entrepot__in=admin_utilisateur.get_accessible_warehouses())
    print(f"\nAdmin user stock access:")
    for stock in admin_stock:
        print(f"  {stock.article.nom}: {stock.quantite} {stock.article.unite} in {stock.entrepot.nom}")
    
    # Test magasinier user can only see stock in Magasin 1
    magasinier_utilisateur = Utilisateur.objects.get(user__username='magasinier1')
    magasinier_stock = Stock.objects.filter(entrepot__in=magasinier_utilisateur.get_accessible_warehouses())
    print(f"\nMagasinier user stock access:")
    for stock in magasinier_stock:
        print(f"  {stock.article.nom}: {stock.quantite} {stock.article.unite} in {stock.entrepot.nom}")
    
    # Test commercial user can see stock in both warehouses
    commercial_utilisateur = Utilisateur.objects.get(user__username='commercial1')
    commercial_stock = Stock.objects.filter(entrepot__in=commercial_utilisateur.get_accessible_warehouses())
    print(f"\nCommercial user stock access:")
    for stock in commercial_stock:
        print(f"  {stock.article.nom}: {stock.quantite} {stock.article.unite} in {stock.entrepot.nom}")
    
    # Test production user can only see stock in Magasin 2
    production_utilisateur = Utilisateur.objects.get(user__username='production1')
    production_stock = Stock.objects.filter(entrepot__in=production_utilisateur.get_accessible_warehouses())
    print(f"\nProduction user stock access:")
    for stock in production_stock:
        print(f"  {stock.article.nom}: {stock.quantite} {stock.article.unite} in {stock.entrepot.nom}")

def test_permission_details():
    """Test detailed permission information"""
    print("\nTesting detailed permissions...")
    
    entrepot1 = Entrepot.objects.get(nom="Magasin 1")
    entrepot2 = Entrepot.objects.get(nom="Magasin 2")
    
    # Show all user-warehouse permissions
    print("\nAll user-warehouse permissions:")
    for user_entrepot in UtilisateurEntrepot.objects.all().select_related('utilisateur', 'entrepot'):
        print(f"  {user_entrepot.utilisateur.nom} -> {user_entrepot.entrepot.nom}: {user_entrepot.permissions_summary}")

def main():
    """Main test function"""
    print("=== Warehouse Permissions Test ===\n")
    
    try:
        # Create test data
        entrepot1, entrepot2, matiere = create_test_data()
        
        # Create test users
        admin_utilisateur, magasinier_utilisateur, commercial_utilisateur, production_utilisateur = create_test_users()
        
        # Test warehouse access
        test_warehouse_access()
        
        # Test stock filtering
        test_stock_filtering()
        
        # Test detailed permissions
        test_permission_details()
        
        print("\n=== Test completed successfully! ===")
        print("\nTest users created:")
        print("  Admin: admin_warehouse / admin123 (access to all warehouses)")
        print("  Magasinier: magasinier1 / magasinier123 (full access to Magasin 1 only)")
        print("  Commercial: commercial1 / commercial123 (read-only access to both warehouses)")
        print("  Production: production1 / production123 (read and modify access to Magasin 2 only)")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 