from django import forms  # import i Forms
from django.contrib.auth.forms import UserCreationForm # Utilizzeremo questo Form per la registrazione Utente ( di modello User )
from django.contrib.auth.models import User # importo Modello User che uso in classe Meta


class FormRegistrazione(UserCreationForm): # creo sottoclasse di UserCreationForm
    email = forms.CharField(max_length=30, required=True, widget=forms.EmailInput()) #aggiungo campo email che in UserCreationForm non è definito(vedi definizione)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2'] # specifico i campi (puoi usare o lista o tuple)