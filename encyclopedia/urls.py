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
    path("wiki/add-page", views.add_page, name="add_page"),
    # Edit the content of an entry
    path("wiki/edit/<str:entry>", views.edit_entry, name="edit_page"),
    # Random entry url 
    path("wiki/random", views.random_entry, name="random_page")

]
