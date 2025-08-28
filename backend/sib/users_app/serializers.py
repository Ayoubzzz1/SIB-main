from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Utilisateur, UtilisateurEntrepot

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',) # L'ID est en lecture seule

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        # Only validate if username is provided and not empty
        if value and value.strip():
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("Un utilisateur avec ce nom existe déjà.")
        return value

    def validate_email(self, value):
        # Only validate if email is provided and not empty
        if value and value.strip():
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},
            'email': {'required': False}
        }

    def validate_username(self, value):
        # Only validate uniqueness if username is being changed and not empty
        if value and value.strip() and self.instance and value != self.instance.username:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("Un utilisateur avec ce nom existe déjà.")
        return value

    def validate_email(self, value):
        # Only validate uniqueness if email is being changed and not empty
        if value and value.strip() and self.instance and value != self.instance.email:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def validate(self, attrs):
        # Only validate fields that are actually provided and not empty
        validated_data = {}
        for field, value in attrs.items():
            if value is not None and value != '' and value.strip():
                validated_data[field] = value
        return validated_data

class UtilisateurEntrepotSerializer(serializers.ModelSerializer):
    entrepot_nom = serializers.CharField(source='entrepot.nom', read_only=True)
    permissions_summary = serializers.CharField(read_only=True)
    
    class Meta:
        model = UtilisateurEntrepot
        fields = ('id', 'entrepot', 'entrepot_nom', 'peut_lire', 'peut_modifier', 'peut_supprimer', 'permissions_summary', 'date_creation')
        read_only_fields = ('id', 'date_creation', 'permissions_summary')

class UtilisateurSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Affiche les détails de l'utilisateur Django lié
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True, required=False
    ) # Permet de lier un User existant lors de la création/mise à jour
    user_data = UserCreateSerializer(write_only=True, required=False) # Pour créer un nouveau User
    user_update_data = UserUpdateSerializer(write_only=True, required=False) # Pour mettre à jour un User existant
    entrepots_autorises = UtilisateurEntrepotSerializer(many=True, read_only=True)
    entrepots_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des entrepôts auxquels l'utilisateur aura accès"
    )
    group_name = serializers.ChoiceField(
        choices=[
            ('Commerciaux', 'Commerciaux'),
            ('Magasiniers', 'Magasiniers'),
            ('Ouvriers de production', 'Ouvriers de production'),
            ('Administrateurs', 'Administrateurs')
        ],
        write_only=True,
        required=False,
        help_text="Groupe Django auquel assigner l'utilisateur"
    )

    class Meta:
        model = Utilisateur
        fields = (
            'id', 'user', 'user_id', 'user_data', 'user_update_data', 
            'nom', 'group_name', 'acces_tous_entrepots', 'cree_le',
            'entrepots_autorises', 'entrepots_ids'
        )
        read_only_fields = ('id', 'cree_le')

    def create(self, validated_data):
        entrepots_ids = validated_data.pop('entrepots_ids', [])
        group_name = validated_data.pop('group_name', None)
        user_data = validated_data.pop('user_data', None)
        user_id = validated_data.pop('user_id', None)

        if user_id:
            user_instance = user_id
        elif user_data:
            # Si un user_data est fourni, créez un User Django
            user_instance = User.objects.create_user(
                username=user_data.get('username'),
                email=user_data.get('email'),
                password=user_data.get('password')
            )
        else:
            raise serializers.ValidationError("Un compte utilisateur Django doit être lié ou créé.")

        # Assign user to group if specified
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                user_instance.groups.add(group)
            except Group.DoesNotExist:
                raise serializers.ValidationError(f"Le groupe '{group_name}' n'existe pas.")

        # Check if a Utilisateur profile was already created by the signal
        try:
            utilisateur = Utilisateur.objects.get(user=user_instance)
            # Update the existing profile with the provided data
            for attr, value in validated_data.items():
                setattr(utilisateur, attr, value)
            utilisateur.save()
        except Utilisateur.DoesNotExist:
            # Create new profile if signal didn't create one
            utilisateur = Utilisateur.objects.create(user=user_instance, **validated_data)
        
        # Create warehouse access permissions
        if entrepots_ids and not utilisateur.acces_tous_entrepots:
            from warehouse.models import Entrepot
            for entrepot_id in entrepots_ids:
                try:
                    entrepot = Entrepot.objects.get(id=entrepot_id)
                    UtilisateurEntrepot.objects.get_or_create(
                        utilisateur=utilisateur,
                        entrepot=entrepot,
                        defaults={
                            'peut_lire': True,
                            'peut_modifier': False,
                            'peut_supprimer': False
                        }
                    )
                except Entrepot.DoesNotExist:
                    pass  # Skip non-existent warehouses
        
        return utilisateur

    def update(self, instance, validated_data):
        entrepots_ids = validated_data.pop('entrepots_ids', None)
        group_name = validated_data.pop('group_name', None)
        user_data = validated_data.pop('user_data', None)
        user_update_data = validated_data.pop('user_update_data', None)
        user_id = validated_data.pop('user_id', None)

        if user_id:
            instance.user = user_id
        elif user_update_data:
            # Mettre à jour le User Django lié
            user_instance = instance.user
            for attr, value in user_update_data.items():
                if value is not None:  # Only update if value is provided
                    if attr == 'password':
                        user_instance.set_password(value)
                    else:
                        setattr(user_instance, attr, value)
            user_instance.save()

        # Update group assignment if specified
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                # Clear existing groups and assign to new group
                instance.user.groups.clear()
                instance.user.groups.add(group)
            except Group.DoesNotExist:
                raise serializers.ValidationError(f"Le groupe '{group_name}' n'existe pas.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update warehouse access permissions
        if entrepots_ids is not None:
            # Clear existing warehouse permissions if not access to all warehouses
            if not instance.acces_tous_entrepots:
                instance.entrepots_autorises.all().delete()
                
                # Create new warehouse access permissions
                from warehouse.models import Entrepot
                for entrepot_id in entrepots_ids:
                    try:
                        entrepot = Entrepot.objects.get(id=entrepot_id)
                        UtilisateurEntrepot.objects.get_or_create(
                            utilisateur=instance,
                            entrepot=entrepot,
                            defaults={
                                'peut_lire': True,
                                'peut_modifier': False,
                                'peut_supprimer': False
                            }
                        )
                    except Entrepot.DoesNotExist:
                        pass  # Skip non-existent warehouses
        
        return instance

    def to_internal_value(self, data):
        """Handle nested user data structure from frontend"""
        if isinstance(data, dict) and 'user' in data and isinstance(data['user'], dict):
            # Convert nested user structure to user_data
            user_data = data.pop('user')
            data['user_data'] = user_data
        return super().to_internal_value(data)
