from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView
from .forms import DiscussioneModelForm, PostModelForm
from .models import Post,Sezione, Discussione
from .mixins import StaffMixin

# Create your views here.

class CreaSezione(StaffMixin, CreateView):
    model = Sezione
    fields = "__all__"
    template_name = "forum/crea_sezione.html"
    success_url = "/"


def visualizza_sezione(request, pk):
    sezione = get_object_or_404(Sezione, pk=pk)
    discussioni_sezione = Discussione.objects.filter(
        sezione_appartenenza=sezione).order_by("-data_creazione")
    context = {"sezione": sezione, "discussioni": discussioni_sezione}
    return render(request, "forum/singola_sezione.html", context)
    

@login_required
def crea_discussione(request, pk):
    sezione = get_object_or_404(Sezione, pk=pk)
    if request.method == "POST":
        form = DiscussioneModelForm(request.POST)
        if form.is_valid():
            discussione = form.save(commit=False)
            discussione.sezione_appartenenza = sezione
            discussione.autore_discussione = request.user
            discussione.save()
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

    paginator = Paginator(posts_discussione, 5)
    page = request.GET.get("pagina")
    posts = paginator.get_page(page)
    
    form_commento = PostModelForm()
    context = {
                "discussione": discussione, 
                "posts_discussione": posts,
                "form_commento": form_commento}
    return render(request, "forum/singola_discussione.html", context)


@login_required
def aggiungi_risposta(request, pk):
    discussione = get_object_or_404(Discussione, pk=pk)
    if request.method == "POST":
        form = PostModelForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.discussione = discussione
            form.instance.autore_post = request.user
            form.save()
            url_discussione = discussione.get_absolute_url()
            pagine_in_discussione = discussione.get_n_pages()
            if pagine_in_discussione > 1:
                success_url = url_discussione + "?pagina=" +str(pagine_in_discussione)
                return HttpResponseRedirect(success_url)
            else:
                return HttpResponseRedirect(url_discussione)
    else:
        return HttpResponseBadRequest()


class CancellaPost(DeleteView):
    model = Post
    success_url = "/"

    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(autore_post_id=self.request.user.id)
