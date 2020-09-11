from django.urls import path
from .views import base,suggestions_view, load_in_db,clear , select_arret, home, load_patterns, download_file, get_choice,load_all,previous_suggestion,selected_view
urlpatterns = [
    path("", home, name="home"),
    path("load_patterns", load_patterns, name="load_patterns"),
    path("load_from_cache/<slug>",load_in_db,name="load-from-cache"),
    path("load_all/", load_all, name="load-all"),
    path("prev_selection",previous_suggestion,name="prev"),
    path("suggestions/<borne_inf>/<borne_sup>/<combinaison>/<selected>", suggestions_view.as_view(), name="suggestions"),
    path("selected/", selected_view.as_view(), name="selected"),
    path("select/<slug>", select_arret, name="select"),
    path("dl_csv", download_file, name="dl_csv"),
    path("clear_db",clear,name="clear"),
    path("get_choice", get_choice, name="get_choice"),
]
