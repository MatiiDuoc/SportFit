"""
URL configuration for SportFit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
<<<<<<< HEAD
from django.urls import path, include
from SportFit_app import views  # Cambiado para importar desde SportFit_app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('__reload__/', include('django_browser_reload.urls')),
=======
from django.urls import path
from SportFit_app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
>>>>>>> 31d95fc2e7ea9e9d39c625ef14f22b960baaeca6
]
