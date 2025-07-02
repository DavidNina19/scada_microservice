from django.shortcuts import render

# Create your views here.
def createGrafico(request):
    return render(request,'index.html')