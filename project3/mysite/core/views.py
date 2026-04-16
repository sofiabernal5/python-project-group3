from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    context = {
        "message": "This came from the view."
        }
    return render(request, 'core/home.html', context)
# Django automatically passes an HttpRequest object as the first argument to any view function that is triggered by a URL match
def records(request):
    records = {
        "record": "record data"
    }
    return records
    


