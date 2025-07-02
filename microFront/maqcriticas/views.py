from django.shortcuts import render

# Create your views here.
def maquinascriticas(request):
    return render(request, 'maquinascriticas.html')