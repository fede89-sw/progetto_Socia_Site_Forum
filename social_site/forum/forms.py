from django import forms
from .models import Discussione, Post
from django.core import validators


class DiscussioneModelForm(forms.ModelForm):
    contenuto = forms.CharField(    # contenuto del primo Post della discussione
        widget=forms.Textarea(attrs={"placeholder": "Di cosa vuoi parlarci?"}),
        max_length=4000, 
        label="Primo Messaggio",
        validators=[validators.MinLengthValidator(10)])
           

    def clean_contenuto(self):
        dati = self.cleaned_data["contenuto"]
        if "cazzo" in dati:
            raise forms.ValidationError("Non scrivere Parolacce!")
        return dati

    class Meta:
        model = Discussione
        fields = ["titolo", "contenuto"]
        widgets = {
            "titolo": forms.TextInput(attrs={"placeholder": "Titolo della Discussione"})
        }


class PostModelForm(forms.ModelForm): # Form per creare i commenti (che sono cmq Post) in usa discussione

    class Meta:
        model = Post
        # solo 'contenuto' in qnt gli altri campi sono dedotti(autore_post è il request.user), la discussione è quella in cui stiamo 
        # creando il Post e la data è automatica
        fields = ["contenuto"]
        # vado ora a specificare degli attributi per la visualizzazione della TextArea 'contenuto' in singola_discussione.html (il commento)
        widgets = {
            "contenuto": forms.Textarea(attrs={"rows": 5}) 
        }
        labels = {
            "contenuto": "Messaggio"
        }
