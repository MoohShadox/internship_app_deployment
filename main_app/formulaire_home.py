from django import forms
from .models import Pattern, Arret
from django.db.models import Max, Min

class form_patterns(forms.Form):


    def __init__(self, *args, **kwargs):
        super(form_patterns, self).__init__(*args, **kwargs)
        max = Arret.objects.aggregate(Max("annee"))["annee__max"]
        min = Arret.objects.aggregate(Min("annee"))["annee__min"]
        if(min == None):
            min = 1800
        if(max == None):
            max = 1801
        year_range = [(i,i) for i in range(min,max+1)]
        self.fields["year_b"] = forms.MultipleChoiceField(label='Année de départ', widget=forms.SelectMultiple,choices=year_range)
        self.fields["year_e"] = forms.MultipleChoiceField(label='Année de fin', widget=forms.SelectMultiple,choices=year_range)
        choices = [(p.name, p.name) for p in Pattern.objects.all()]
        self.fields["choice"] = forms.MultipleChoiceField(label="Filtres",widget=forms.CheckboxSelectMultiple, choices=choices)
        self.fields["conjonction"] = forms.ChoiceField(label='Type de combinaison',
                                                               widget=forms.RadioSelect,
                                                               choices=[("Conjonction", "Conjonction"),
                                                                        ("Disjonction", "Disjonction")]
                                                               )

