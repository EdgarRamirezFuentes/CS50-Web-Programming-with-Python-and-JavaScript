from logging import PlaceHolder
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms

from . import util
import markdown2

class SearchEntryForm(forms.Form):
    entry = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia', 'class' : 'search'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form" : SearchEntryForm()
    })

def entry_page(request, entry):
    '''
        Show the requested entry information in a page
    '''
    # Get the Entry Markdown content
    entry_content = util.get_entry(entry)

    if not entry_content:
        # The requested entry does not exist and show an error page
        return render(request, "encyclopedia/error_page.html", {
            "entry" : entry,
            "message" : f"The page {entry} was not found!",
            "form" : SearchEntryForm()
        })
    
    # Convert from Markdown to HTML
    entry_content = markdown2.markdown(entry_content)
    return render(request, "encyclopedia/entry_page.html", {
        "entry" : entry,
        "entry_content" : entry_content,
        "form" : SearchEntryForm()
    })

def search_entry(request):
    if request.method == "POST":
        form = SearchEntryForm(request.POST)
        if form.is_valid():
            # Get the entry value
            entry = form.cleaned_data["entry"]
            # Get the Entry markdown content
            entry_content = util.get_entry(entry.lower())
            if entry_content:
                # Redirect to the requested entry page if the content does exist
                return HttpResponseRedirect(reverse("encyclopedia:entry_page", kwargs={"entry" : entry}))
            if entry and not entry_content:
                # The user requested a non-empty entry, but it does not exist
                similar_entries = util.get_similar_entries(entry)
                return render(request, "encyclopedia/search_results.html", {
                    "similar_entries" : similar_entries,
                    "form" : SearchEntryForm(),
                    "entry" : entry
                })
    # Return to the index page if the entry is empty
    return HttpResponseRedirect(reverse("encyclopedia:index"))