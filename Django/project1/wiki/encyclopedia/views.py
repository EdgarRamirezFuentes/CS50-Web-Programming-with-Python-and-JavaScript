from django.shortcuts import render
from . import util
import markdown2

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
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
            "entry" : entry
        })
    
    # Convert from Markdown to HTML
    entry_content = markdown2.markdown(entry_content)
    return render(request, "encyclopedia/entry_page.html", {
        "entry" : entry,
        "entry_content" : entry_content
    })

