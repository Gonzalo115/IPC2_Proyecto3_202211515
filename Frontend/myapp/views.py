from django.shortcuts import render, redirect

import requests
import xml.etree.ElementTree as ET

from django.http import HttpResponse, JsonResponse

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

url = "http://localhost:5000"
# Create your views here.

# Create your views here.
def index(request):
    return render(request, "index.html")

def help(request):
    return render(request, "help.html")

def add(request):
    if request.method == "POST":
        # Recoger datos del formulario
        correo = request.POST.get('correo')
        nombre = request.POST.get('nombre')
        alias = request.POST.get('alias')
        split = request.POST.get('split')
        
        # Crear estructura XML
        datos = Element('datos')
        dato = SubElement(datos, 'dato')
        SubElement(dato, 'correo').text = correo
        SubElement(dato, 'nombre', alias=split).text = f"{nombre} {split}{alias}"
        
        # Convertir a string
        xml_string = parseString(tostring(datos)).toprettyxml(indent="   ")
        
        # Hacer petición a la API
        api_url = url + "/process"
        headers = {
            'Content-Type': 'application/xml'  # Suponiendo que la API espera XML
        }
        response = requests.post(api_url, data=xml_string, headers=headers)
        
        # Aquí puedes manejar la respuesta como lo necesites
        if response.status_code == 200:
           return redirect('list')
        else:
            return HttpResponse("Error al enviar datos", status=400)
    else:
        # Renderizar formulario si es GET u otro método
        return render(request, 'add.html')


def stats(request):
    contexto = {
        'response': {}
    }
    response = requests.get(url + "/stats")
    
    if response.status_code == 200:
        contexto['response'] = response.json()
        
    return render(request, "stats.html", contexto)



def listhast(request):
    query = request.GET.get('inputSearch')
    print(query)
    contexto = {
        'hashtags': [],
        'query': query
    }

    # Comprobar si hay una búsqueda
    if query:
        # Si hay un término de búsqueda, buscar por alias
        response = requests.get(url + f"/search-by-date-hashtags/{query}")
    else:
        # Si no hay término de búsqueda, obtener todos los datos
        response = requests.get(url + "/lista")

    if response.status_code == 200:
        contexto['hashtags'] = response.json()
    else:
        # Puedes manejar errores específicos aquí si lo deseas
        pass  # O quizás mostrar un mensaje de error

    return render(request, "listhast.html", contexto)


def listmension(request):
    query = request.GET.get('inputSearch')
    contexto = {
        'hashtags': [],
        'query': query
    }

    # Comprobar si hay una búsqueda
    if query:
        # Si hay un término de búsqueda, buscar por alias
        response = requests.get(url + f"/search-by-date-mentions/{query}")
    else:
        # Si no hay término de búsqueda, obtener todos los datos
        response = requests.get(url + "/lista")

    if response.status_code == 200:
        contexto['hashtags'] = response.json()
    else:
        # Puedes manejar errores específicos aquí si lo deseas
        pass  # O quizás mostrar un mensaje de error

    return render(request, "listmension.html", contexto)


def listfeelings(request):
    query1 = request.GET.get('inputSearch')
    query2 = request.GET.get('inputSearch2')
    query = f'{query1}-{query2}'
    print(query)

    contexto = {
        'feelings': [],
        'query': query
    }

    # Comprobar si hay una búsqueda
    if query:
        # Si hay un término de búsqueda, buscar por alias
        response = requests.get(url + f"/search-by-date-feelings/{query}")
    else:
        # Si no hay término de búsqueda, obtener todos los datos
        response = requests.get(url + "/lista")

    if response.status_code == 200:
        contexto['feelings'] = response.json()
    else:
        # Puedes manejar errores específicos aquí si lo deseas
        pass  # O quizás mostrar un mensaje de error

    return render(request, "listfeelings.html", contexto)


def palabra(request):
    response_content = None
    if request.method == "POST":
        xml_file = request.FILES.get('xmlFile')  # Obtener el archivo XML cargado
        if xml_file:
            content = xml_file.read().decode('utf-8')  # Leer y decodificar el contenido del archivo
            print(content)
            # Hacer petición a la API
            api_url = url + "/processWords"
            headers = {
                'Content-Type': 'application/xml'  # Suponiendo que la API espera XML
            }
            response = requests.post(api_url, data=content, headers=headers)
            
            # Aquí puedes manejar la respuesta como lo necesites
            if response.status_code == 200:
                response_content = response.text
            else:
                # Puedes manejar errores de manera más específica aquí si lo necesitas
                return JsonResponse({"error": "Error al enviar datos a la API."}, status=400)
    return render(request, 'palabra.html', {'response_content': response_content})  # Enviar el contenido de la respuesta al template

def mensaje(request):
    response_content = None
    if request.method == "POST":
        xml_file = request.FILES.get('xmlFile')  # Obtener el archivo XML cargado
        if xml_file:
            content = xml_file.read().decode('utf-8')  # Leer y decodificar el contenido del archivo
            # Hacer petición a la API
            api_url = url + "/processMessage"
            headers = {
                'Content-Type': 'application/xml'  # Suponiendo que la API espera XML
            }
            response = requests.post(api_url, data=content, headers=headers)
            
            # Aquí puedes manejar la respuesta como lo necesites
            if response.status_code == 200:
                response_content = response.text
            else:
                # Puedes manejar errores de manera más específica aquí si lo necesitas
                return JsonResponse({"error": "Error al enviar datos a la API."}, status=400)
    return render(request, 'mensaje.html', {'response_content': response_content})  # Enviar el contenido de la respuesta al template        