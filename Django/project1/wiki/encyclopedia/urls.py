from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # Entry page
    path("wiki/<str:entry>", views.entry_page, name="entry_page")
]
