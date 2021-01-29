from typing import no_type_check_decorator
from django.db import models
from django.contrib.auth.models import User # sono gli Utenti a creare nuovi Post e Discussioni
from django.urls import reverse
import math

# Create your models here.

class Sezione(models.Model):
    """ 
    Le sezioni dividono il sito per categorie di discussione.
    Ciascuna sezione contiene svariate discussioni.
    Create dagli amministratori del sito.
    """
    nome_sezione = models.CharField(max_length=80)
    descrizione = models.CharField(max_length=150, blank=True, null=True) # black e null permettono di lasciare vuoto qst campo, se desiderato
    logo_sezione = models.ImageField(blank=True, null=True)
    # non abbiamo bisogno di un campo 'Utente' perchè sono sono gli amminitratori che creano le sezioni

    def __str__(self):
        return self.nome_sezione

    def get_absolute_url(self):
        return reverse("sezione_view", kwargs={"pk": self.pk})

    def get_last_discussions(self): 
        # metodo per avere le ultime 2 discussioni più recenti da mostrare nelle card dell'homepage 
        return Discussione.objects.filter(sezione_appartenenza=self).order_by("-data_creazione")[:2]
        # senza usare la lista [:2] che mi restituisce dall'inizio della lista al secondo oggetto, potevo fare poi nel ciclo for del template
        # dove visualizzo i risultati, un if forloop.counter <= 2 , ed avevo cmq i primi 2 oggetti.


    def get_number_of_posts_in_section(self): 
        # metodo per avere il numero totale di Post presenti in una sezione, compreso ogni Post in ogni Discussione della Sezione
        return Post.objects.filter(discussione__sezione_appartenenza=self).count()
        """ andiamo a filtrare tra tutti gli oggetti di tipo Post, di cui vogliamo filtrare quelli che fanno parte di una Discussione
            la cui Sezione di appartenenza corrisponde a self (l'istanze della Sezione da cui stiamo richiamndo il metodo )"""

    class Meta:
        verbose_name = "Sezione"
        verbose_name_plural = "Sezioni"
    

class Discussione(models.Model):
    titolo = models.CharField(max_length=120)
    data_creazione = models.DateTimeField(auto_now_add=True) # data viene inserita alla creazione
    autore_discussione = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussioni")
    sezione_appartenenza = models.ForeignKey(Sezione, on_delete=models.CASCADE)

    def __str__(self):
        return self.titolo

    def get_absolute_url(self):
        return reverse("visualizza_discussione", kwargs={"pk": self.pk})

    def get_n_pages(self):
        """ ritorna il numero di pagine, paginated by 5, che ha la discussione """
        posts_discussione = self.post_set.count() # prendo il numero totale di Post per la discussion
        # math.ceil= Arrotonda un numero per eccesso al numero intero più vicino
        n_pagine = math.ceil(posts_discussione/5)
        return n_pagine
    
    class Meta:
        verbose_name = "Discussione"
        verbose_name_plural = "Discussioni"


class Post(models.Model):
    autore_post = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    contenuto = models.TextField()
    data_creazione = models.DateTimeField(auto_now_add=True)
    discussione = models.ForeignKey(Discussione, on_delete=models.CASCADE)

    def __str__(self):
        return self.autore_post.username # metto anche username se nò quando inserisco un post mi dà errore in qnt __str__ torna un oggetto di tipo User e non una stringa (altrimenti per il sito andava bene anche solo self.autore_post)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"