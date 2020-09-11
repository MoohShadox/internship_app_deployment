from django import forms
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
import os
import pandas as pd
from .models import Arret, Pattern
from django.db.models import Q
from django.views.generic import ListView
from .formulaire_home import form_patterns
import mimetypes
from django.contrib import messages

# Create your views here.


def base(request):
    return render(request,"base.html")

def clear(request):
    Arret.objects.all().delete()
    return render(request,"base.html")

def load_all(request):
    file_list = os.listdir(settings.CACHE_ROOT)
    for file in file_list:
        print("Année en cours : ",file)
        L = os.listdir(settings.CACHE_ROOT + "/" + file)
        for id, csv_file in enumerate(L):
            df = pd.read_csv(settings.CACHE_ROOT + "/" + file + "/" + csv_file, sep=";", index_col=0)
            for i in df.index:
                A = Arret()
                A.date = df["date"][i]
                A.annee = file
                A.num_receuil = id
                if("page" in df):
                    A.page = df["page"][i]
                else:
                    A.page = 1
                A.contenu = df["arrêt"][i]
                A.juridiction = df["juridiction"][i]
                A.image = df["lien"][i]
                A.identifiant = i
                A.save()

    return render(request, "loaded_success.html")

def load_in_db(request,slug):
    L = os.listdir(settings.CACHE_ROOT + "/" + slug)
    for id,csv_file in enumerate(L):

        df = pd.read_csv(settings.CACHE_ROOT + "/" + slug + "/" + csv_file, sep=";",index_col=0)

        #R = Receuil()
        #R.nom = slug + str(id)

        for arret, annee, juridiction, page, identifiant, image in zip(df["arrêt"], df["date"], df["juridiction"], df["page"],df.index,df["lien"]):

            A = Arret()
            A.date = annee
            A.annee = slug
            A.num_receuil = id
            A.page = page
            A.contenu = arret
            A.juridiction = juridiction
            A.image = image
            A.identifiant = identifiant
            A.save()

            #R.arrets.add(A)
            #R.save()


    return render(request, "loaded_success.html")



class suggestions_view(ListView):
    template_name = "suggestions_table.html"
    paginate_by = 10

    def get_queryset(self):
        patterns = Pattern.objects.filter(selected=True)
        result = Arret.objects.none()
        if(self.kwargs["combinaison"] == "Conjonction"):
            result = Arret.objects.filter(annee__gte=self.kwargs["borne_inf"],annee__lte=self.kwargs["borne_sup"])
            for p in patterns:
                result = result.filter(contenu__regex=p.pattern)
        else:
            for p in patterns:
                result = result | Arret.objects.filter(contenu__regex=p.pattern, annee__gte=self.kwargs["borne_inf"], annee__lte=self.kwargs["borne_sup"])
        if(self.kwargs["selected"]=="True"):
        	result = result.filter(selected = False)
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['display_selected'] = self.kwargs["selected"] == "True"
        context["borne_inf"] = self.kwargs["borne_inf"]
        context["borne_sup"] = self.kwargs["borne_sup"]
        context["combinaison"] = self.kwargs["combinaison"]

        return context




def select_arret(request,slug):
    article_qs = Arret.objects.filter(identifiant=slug)
    if(article_qs.exists()):
        article = article_qs[0]
        article.selected = not article.selected
        if article.selected:
            article.Armes_juridictionnelles = article.get_armes_juridictionnelles()
        article.save()
    return HttpResponse(status=204)



def download_file(request):
    qs = Arret.objects.filter(selected=True)
    output_path = "output.csv"
    if(qs.exists()):
        df = pd.DataFrame.from_records( qs.values_list("annee","Armes_juridictionnelles","contenu", "date", "juridiction", 'page', 'image'))   
        df = df.rename(columns={0 : "Année du receuil", 1: "Armes_juridictionnelles", 2: "Arrêt", 3: "Date", 4: "Juridiction", 5:"Page", 6: "Lien"}, errors="raise")    
        df.to_csv(output_path, encoding="utf-8", sep = ";")
        fl = open(output_path, "r")
        mime_type, _ = mimetypes.guess_type(output_path)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % output_path
        os.remove(output_path)
        return response
    return HttpResponse(status=404)


def load_patterns(request):
    names = ["évidence", "abrogation", "nécessité", "négation", "conditionnel",
     "législateur/loi n’a pu", "législateur/loi ne peut", " silence de la loi ", " impossible de ne pas ", " suppléer à la loi ",
     " implicitement", " virtuellement ", "aboli" ,"jurisconsultes"]
    patterns = [r" évid\S+", r" abrog\S+", r" nécess\S+", r" n(e\s|')(\S+?\s){1,5}pas ", r"[a-zA-Z]+?(rais|rait|rions|riez|raient) ", " (l(é|e)gislateur|loi) n'a pu ",
     " (l(é|e)gislateur|loi) ne peut ", " silence de la loi ", " impossible de ne pas ", " suppl(é|e)er (à|a) la loi ",
      " implicitement ", " virtuellement ", " aboli\S+", " jurisconsultes "]
    for name, pattern in zip( names, patterns):
        P = Pattern()
        P.name = name
        P.pattern = pattern
        P.selected = False
        P.save()
    return render(request, "loaded_success_patterns.html")

def get_choice(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = form_patterns(request.POST)
        if form.is_valid():
            pattern_names = form.cleaned_data.get('choice')
            Patterns = Pattern.objects.all()
            for p in Patterns:
                if p.name in pattern_names:
                    p.selected = True
                else:
                    p.selected = False
                p.save()

            year_inf = form.cleaned_data.get('year_b')[0]
            year_sup = form.cleaned_data.get('year_e')[0]

            if(year_sup <= year_inf):
                messages.error(request,"Il faut que l'année de fin soit aprés l'année de début !")
                return redirect("core:home")

            settings.YEAR_INF = form.cleaned_data.get('year_b')[0]
            settings.YEAR_SUP = form.cleaned_data.get('year_e')[0]
            settings.DEFAULT_COMBINAISON = form.cleaned_data.get('conjonction')

            # redirect to a new URL:
            return redirect("core:suggestions", borne_inf=year_inf , borne_sup = year_sup,combinaison=form.cleaned_data.get('conjonction'),selected = True)
        else:
            messages.error(request,"Quelque chose cloche dans le formulaire")
            return redirect("core:home")




def previous_suggestion(request):
    return redirect("core:suggestions", borne_inf=settings.YEAR_INF , borne_sup = settings.YEAR_SUP,combinaison=settings.DEFAULT_COMBINAISON, selected=True)

class selected_view(ListView):
    template_name = "selected_table.html"
    paginate_by = 10

    def get_queryset(self):
        result = Arret.objects.filter(selected=True)
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['display_selected'] = True
        return context


def home(request):
    from .formulaire_home import form_patterns
    Form = form_patterns()

    Form.choices = [(p.name,p.name) for  p in Pattern.objects.all()]
    Form.choice = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                             choices=Form.choices)
    context = {"form" : Form}
    return render(request, "home.html", context = context)
