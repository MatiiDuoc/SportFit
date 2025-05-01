from django.shortcuts import render
from django.http import HttpResponse
import json
# Create your views here.
#home
def home(request):
    return render(request, 'home.html')

#administrador
def dashboard_administrador(request):
     # Datos de ejemplo (pueden venir de la base de datos)
    ventas = [1200, 1900, 3000, 5000]
    semanas = ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4']

    # Pasar los datos al contexto
    context = {
        'ventas': json.dumps(ventas),  # Convertir a JSON para usar en JavaScript
        'semanas': json.dumps(semanas),
    }
    return render(request, 'admin/dashboard.html')
