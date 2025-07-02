from django.shortcuts import render

# Create your views here.
def frontdetalle(request):
    return render(request, 'principal.html')