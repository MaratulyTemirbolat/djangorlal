# Django modules
from django.contrib import admin
from django.urls import path

# Project modules
from apps.tasks.views import hello_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path(route="hello/", view=hello_view, name="hello-view"),
]
