
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
from django.urls import path,include

from internship_law_extr import settings

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path("", include(("main_app.urls","main_app"), namespace='core')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)