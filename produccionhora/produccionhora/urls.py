"""
URL configuration for produccionhora project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from pxh.views import ProductionPerHourAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/<str:area>/<str:codmaq>/<str:fecha_inicio_str>/<str:fecha_fin_str>/<str:hora_inicio_str>/<str:minute_inicio_str>/<str:hora_fin_str>/<str:minute_fin_str>/', ProductionPerHourAPIView.as_view(), name='produccionhora'),
]
