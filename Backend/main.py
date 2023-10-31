from flask import Flask, request, jsonify, Response
from xml.etree import ElementTree as ET
import re
import os

app = Flask(__name__)



XML_Palabras = 'db_palabras.xml'
XML_Mensajes = 'db_mensaje.xml'

@app.route('/')
def index():
    return "API de Flask de la empresa Tecnologías Chapinas, S.A."

#/process
@app.route('/processWords', methods=['POST'])
def process_xml():
    xml_data = request.data
    root = ET.fromstring(xml_data)
    PALABRAS_POSITIVAS = 0
    PALABRAS_POSITIVAS_RECHAZADA = 0
    PALABRAS_NEGATIVAS = 0
    PALABRAS_NEGATIVAS_RECHAZADA = 0


    # Cargar XML existente
    if os.path.exists(XML_Palabras):
        tree = ET.parse(XML_Palabras)
        diccionario = tree.getroot()
        sentimientos_p = diccionario.find('sentimientos_positivos')
        sentimientos_n = diccionario.find('sentimientos_negativos')
    else:
        diccionario = ET.Element("diccionario")
        sentimientos_p = ET.SubElement(diccionario, "sentimientos_positivos")
        sentimientos_n = ET.SubElement(diccionario, "sentimientos_negativos")

    sentimientos_positivos = root.find('sentimientos_positivos')

    for palabraP in sentimientos_positivos.findall('palabra'):
        repetida = False
        palabra = palabraP.text
        print(palabra)
        objPositiva = {
            'Palabra': palabra
        }
        #Agregar la palabra Positiva

        
        for c in sentimientos_p.findall('palabra'):
            word = c.text
            if word == objPositiva['Palabra']:
                PALABRAS_POSITIVAS_RECHAZADA += 1
                repetida = True
                break

        for c in sentimientos_n.findall('palabra'):
            word = c.text
            if word == objPositiva['Palabra']:
                PALABRAS_POSITIVAS_RECHAZADA += 1
                repetida = True
                break

        if repetida == False:
            ET.SubElement(sentimientos_p, "palabra").text = objPositiva['Palabra']
            PALABRAS_POSITIVAS += 1


    sentimientos_negativos = root.find('sentimientos_negativos')

    for palabraN in sentimientos_negativos.findall('palabra'):
        repetida = False
        palabra = palabraN.text
        objNegativa = {
            'Palabra': palabra
        }

        #Validar si ya existe
        for c in sentimientos_p.findall('palabra'):
            word = c.text
            if word == objNegativa['Palabra']:
                PALABRAS_NEGATIVAS_RECHAZADA += 1
                repetida = True
                break
        for c in sentimientos_n.findall('palabra'):
            word = c.text
            if word == objNegativa['Palabra']:
                PALABRAS_NEGATIVAS_RECHAZADA += 1
                repetida = True
                break

        #Agregar la palabra Negativa 
        if repetida == False:
            ET.SubElement(sentimientos_n, "palabra").text = objNegativa['Palabra']
            PALABRAS_NEGATIVAS +=1

    # Guardar XML
    tree = ET.ElementTree(diccionario)
    tree.write(XML_Palabras)

    #Respuesta 
    response_content = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <PALABRAS_POSITIVAS>{}</PALABRAS_POSITIVAS>
    <PALABRAS_POSITIVAS_RECHAZADA>{}</PALABRAS_POSITIVAS_RECHAZADA>
    <PALABRAS_NEGATIVAS>{}</PALABRAS_NEGATIVAS>
    <PALABRAS_NEGATIVAS_RECHAZADA>{}</PALABRAS_NEGATIVAS_RECHAZADA>
</response>""".format(PALABRAS_POSITIVAS, PALABRAS_POSITIVAS_RECHAZADA, PALABRAS_NEGATIVAS, PALABRAS_NEGATIVAS_RECHAZADA)
    
    return Response(response_content, content_type='application/xml; charset=utf-8')





if __name__ == '__main__':
    app.run(debug=True)
