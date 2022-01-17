from unicodedata import name
from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    # Entry page url
    path("wiki/info/<str:entry>", views.entry_page, name="entry_page"),
    # Search entry url
    path("wiki/search", views.search_entry, name="search_entry"),
    # Add a new page
    path("wiki/add-page", views.add_page, name="add_page")
]
