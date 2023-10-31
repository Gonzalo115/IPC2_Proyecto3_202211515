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
        palabra = palabraP.text
        print(palabra)
        objPositiva = {
            'Palabra': palabra
        }


        ET.SubElement(sentimientos_p, "palabra").text = objPositiva['Palabra']

    sentimientos_negativos = root.find('sentimientos_negativos')


    for palabraN in sentimientos_negativos.findall('palabra'):
        palabra = palabraN.text
        print(palabra)
        objNegativa = {
            'Palabra': palabra
        }
        
        ET.SubElement(sentimientos_n, "palabra").text = objNegativa['Palabra']

    # Guardar XML
    tree = ET.ElementTree(diccionario)
    tree.write(XML_Palabras)

    return jsonify({"message": "XML procesado con éxito"})





if __name__ == '__main__':
    app.run(debug=True)
