from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView
from .forms import DiscussioneModelForm, PostModelForm
from .models import Post,Sezione, Discussione
from .mixins import StaffMixin

# from django.views.generic.detail import DetailView 

# Create your views here.

class CreaSezione(StaffMixin, CreateView):
    model = Sezione # voglio permettere ad un amminitratore di creare una Sezione da sito
    fields = "__all__"
    template_name = "forum/crea_sezione.html"
    success_url = "/"


def visualizza_sezione(request, pk):
    sezione = get_object_or_404(Sezione, pk=pk)
    discussioni_sezione = Discussione.objects.filter(
        sezione_appartenenza=sezione).order_by("-data_creazione") # ordina le discussioni dalla più recente alla meno
    context = {"sezione": sezione, "discussioni": discussioni_sezione}
    return render(request, "forum/singola_sezione.html", context)
    

@login_required # decoratore django per avere un utente loggato per usare la view
def crea_discussione(request, pk):
    sezione = get_object_or_404(Sezione, pk=pk) # andiamo a prendere la sezione di appartenenza della nostra discussione
    if request.method == "POST":
        form = DiscussioneModelForm(request.POST)
        if form.is_valid():
            discussione = form.save(commit=False) # commit=False vuol dire di aspettare a salvare il Form
            # aspetto a salvare perchè olte i campi titolo e discussione immessi tramite Form, nel Model 'Discussione' dobbiamo salvare
            # 'sezione_appartenenza' e 'autore_discussione'
            discussione.sezione_appartenenza = sezione # sezione presa nella prima riga della view, tramite URL nella barra indirizzi
            discussione.autore_discussione = request.user # autore è l'utente autenticato al momento della creazione
            discussione.save()
            # vado poi a creare il primo Post
            primo_post = Post.objects.create(
                autore_post=request.user, 
                contenuto=form.cleaned_data["contenuto"], 
                discussione=discussione)
            return HttpResponseRedirect(discussione.get_absolute_url())
    else:
        form = DiscussioneModelForm()
    context = {"form": form, "sezione": sezione}
    return render(request, "forum/crea_discussione.html", context)


def visualizza_discussione(request, pk):
    discussione = get_object_or_404(Discussione, pk=pk)
    posts_discussione = Post.objects.filter(discussione=discussione)

    # Paginator: https://docs.djangoproject.com/en/3.1/topics/pagination/#using-paginator-in-a-view-function
    paginator = Paginator(posts_discussione, 5)
    page = request.GET.get("pagina") # prendo il valore della pagina corrispondente, dalla barra degli URL tramite GET
    posts = paginator.get_page(page) # chiamo il metodo get_page dell'istanza paginator a cui passo la pagina in cui ci troviamo
    
    form_commento = PostModelForm() # aggiungo il Form dei commenti, per visualizzarlo nella discussione ("pagina" è il nome dato da noi)  
    context = {
                "discussione": discussione, 
                # "posts_discussione": posts_discussione, ->Non passo più tutti i post della discussione, ma posts , una 'sotto-queryset' con gli elementi della pagina che stiamo visualizzando
                "posts_discussione": posts,
                "form_commento": form_commento}
    return render(request, "forum/singola_discussione.html", context)


@login_required
def aggiungi_risposta(request, pk): # aggiungi risposta ( Post ) ad una discussione
    discussione = get_object_or_404(Discussione, pk=pk) # prendo la discussione in cui è mi trovo, in cui verrà aggiunto il commento/Post
    if request.method == "POST":
        """ in qst view accettiamo solo una richiesta di tipo POST, in quanto passeremo il Form 'PostModelForm' alla view
            'visualizza_discussione', essendo un commento parte integrante della discussione, e non una pagina a sé """
        form = PostModelForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.discussione = discussione
            form.instance.autore_post = request.user
            form.save()
            """ non avendo assegnato 'form.save()' ad una variabile come fatto in 'crea_discussione', uso form.instance
                (istanza del form PostModelForm). Potevo infatti fare:
                commento = form.save(commit=False)
                commento.discussione = discussione
                commento.autore_post = request.user
                commento.save() """
            url_discussione = discussione.get_absolute_url()
            pagine_in_discussione = discussione.get_n_pages()
            if pagine_in_discussione > 1:
                success_url = url_discussione + "?pagina=" +str(pagine_in_discussione)
                return HttpResponseRedirect(success_url) # una volta commentato, reindirizzo alla stessa pagina 'discussione' in cui ho commentato, però all'ultima pagina, se n_pagine >1
            else:
                return HttpResponseRedirect(url_discussione)# se non c'è le pagine non sono >1, reindirizzo alla pagina della discussione
    else:
        """ se la richiesta non è POST solleviamo un'eccezione. In verità chiamiamo la funzione 'HttpResponseBadRequest', che risponde
        con lo status_code relativo, del modello Http. Questo perchè a noi non interessano altre richieste, vogliamo solo aggiungere
        dati alla discussione. Passeremo il form alla view 'visualizza_discussione' """
        return HttpResponseBadRequest()


class CancellaPost(DeleteView):
    model = Post
    success_url = "/" # URL di reindirizzamento a cancellazione avvenuta

    
    def get_queryset(self):
        """ vogliamo che un utente possa cancellare solo i propri post. Possiamo farlo con i Mixins o sovrascrivendo il metodo 'get_queryset'
            che 'DeleteView' eredita da 'SingleObjectMixin' """
        queryset = super().get_queryset()
        return queryset.filter(autore_post_id=self.request.user.id)