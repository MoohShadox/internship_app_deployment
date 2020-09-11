from django.db import models

from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.conf import settings
import re

class Pattern(models.Model):
    name = models.CharField(max_length = 70,primary_key=True)
    pattern = models.CharField(max_length= 70)
    selected = models.BooleanField(default = False)

class Arret(models.Model):
    identifiant = models.SlugField(primary_key=True)
    date = models.CharField(max_length=20)
    juridiction = models.CharField(max_length=200)
    page = models.IntegerField()
    contenu = models.TextField()
    image = models.URLField()
    annee = models.IntegerField()
    num_receuil = models.IntegerField()
    selected = models.BooleanField(default=False)
    Armes_juridictionnelles = models.TextField(default = "")

    #TODO
    def highlights(self):
        patterns = Pattern.objects.filter(selected = True)
        text = self.contenu
        for p in patterns:
          p = re.compile(p.pattern)
          count = 0
          for m in p.finditer(text):
            start, end = m.span()
            start += count*7
            end += count*7
            text = text[:start]+ "<b>" + text[start:end ] + "</b>" + text[end : ] 
            count += 1
        return mark_safe(text)

    def get_selection_url(self):

        return reverse("core:select", )

    def select(self):
        self.selected = not self.selected
        if self.selected:
            self.Armes_juridictionnelles = self.get_armes_juridictionnelles()

    def get_armes_juridictionnelles(self):
        patterns = Pattern.objects.filter(selected = True)
        text = self.contenu
        l = ""
        for p in patterns:

            if re.search(p.pattern, text) is not None:
                l += "," + p.name
        return l[1:]




