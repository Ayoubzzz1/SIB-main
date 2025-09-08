from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

# Custom User Creation Form with better field organization
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email optional (not required)
        self.fields['email'].required = False
        # Add help text
        self.fields['username'].help_text = "Nom d'utilisateur unique pour la connexion"
        self.fields['email'].help_text = "Adresse électronique de l'utilisateur (optionnel)"
        self.fields['first_name'].help_text = "Prénom de l'utilisateur"
        self.fields['last_name'].help_text = "Nom de famille de l'utilisateur"
