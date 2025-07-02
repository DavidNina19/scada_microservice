from django.shortcuts import render

# Create your views here.
def frontCircutor(request):
    return render(request, 'principal.html')