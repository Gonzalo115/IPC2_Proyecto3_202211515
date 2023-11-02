from flask import Flask, request, jsonify, Response
from xml.etree import ElementTree as ET
import re
import os
import xml.dom.minidom
from fechastem import fechastem
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)



XML_Palabras = 'db_palabras.xml'
XML_Mensajes = 'db_mensaje.xml'

@app.route('/')
def index():
    return "API de Flask de la empresa Tecnologías Chapinas, S.A."

#/process
@app.route('/processWords', methods=['POST'])
def process_xml():
    xml_data = request.data.decode('utf-8')
    if not xml_data.endswith('</diccionario>'):
        xml_data += '>'

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
        palabra = palabraP.text.strip()
        palabra = palabra.lower()
        objPositiva = {
            'Palabra': palabra
        }
        #Agregar la palabra Positiva

        
        for c in sentimientos_p.findall('palabra'):
            word = c.text
            if word == objPositiva['Palabra'] or son_iguales_con_o_sin_tildes(word, objPositiva['Palabra']):
                PALABRAS_POSITIVAS_RECHAZADA += 1
                repetida = True
                break

        for c in sentimientos_n.findall('palabra'):
            word = c.text
            if word == objPositiva['Palabra'] or son_iguales_con_o_sin_tildes(word, objPositiva['Palabra']):
                PALABRAS_POSITIVAS_RECHAZADA += 1
                repetida = True
                break

        if repetida == False:
            ET.SubElement(sentimientos_p, "palabra").text = objPositiva['Palabra']
            PALABRAS_POSITIVAS += 1


    sentimientos_negativos = root.find('sentimientos_negativos')

    for palabraN in sentimientos_negativos.findall('palabra'):
        repetida = False
        palabra = palabraN.text.strip()
        palabra = palabra.lower()
        objNegativa = {
            'Palabra': palabra
        }

        #Validar si ya existe
        for c in sentimientos_p.findall('palabra'):
            word = c.text
            if word == objNegativa['Palabra'] or son_iguales_con_o_sin_tildes(word, objNegativa['Palabra']):
                PALABRAS_NEGATIVAS_RECHAZADA += 1
                repetida = True
                break

        for c in sentimientos_n.findall('palabra') :
            word = c.text
            if word == objNegativa['Palabra'] or son_iguales_con_o_sin_tildes(word, objNegativa['Palabra']):
                PALABRAS_NEGATIVAS_RECHAZADA += 1
                repetida = True
                break

        #Agregar la palabra Negativa 
        if repetida == False:
            ET.SubElement(sentimientos_n, "palabra").text = objNegativa['Palabra']
            PALABRAS_NEGATIVAS +=1

    # Guardar XML
    tree = ET.ElementTree(diccionario)
    tree.write(XML_Palabras, encoding="utf-8")

    #Respuesta 
    response_content = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <PALABRAS_POSITIVAS>{}</PALABRAS_POSITIVAS>
    <PALABRAS_POSITIVAS_RECHAZADA>{}</PALABRAS_POSITIVAS_RECHAZADA>
    <PALABRAS_NEGATIVAS>{}</PALABRAS_NEGATIVAS>
    <PALABRAS_NEGATIVAS_RECHAZADA>{}</PALABRAS_NEGATIVAS_RECHAZADA>
</response>""".format(PALABRAS_POSITIVAS, PALABRAS_POSITIVAS_RECHAZADA, PALABRAS_NEGATIVAS, PALABRAS_NEGATIVAS_RECHAZADA)
    
    return Response(response_content, content_type='application/xml; charset=utf-8'), 200


def quitar_tildes(palabra):
    # Diccionario de equivalencias de letras con tildes a letras sin tildes
    equivalencias = {
        'á': 'a',
        'é': 'e',
        'í': 'i',
        'ó': 'o',
        'ú': 'u',
        'Á': 'A',
        'É': 'E',
        'Í': 'I',
        'Ó': 'O',
        'Ú': 'U',
    }

    # Reemplaza las letras con tildes por sus equivalentes sin tildes
    for tildada, sin_tilde in equivalencias.items():
        palabra = palabra.replace(tildada, sin_tilde)

    return palabra

def son_iguales_con_o_sin_tildes(palabra1, palabra2):
    # Quita las tildes de ambas palabras y compáralas
    palabra1_sin_tilde = quitar_tildes(palabra1)
    palabra2_sin_tilde = quitar_tildes(palabra2)

    return palabra1_sin_tilde == palabra2_sin_tilde 



@app.route('/processMessage', methods=['POST'])
def process_xml2():
    xml_data = request.data.decode('utf-8')
    if not xml_data.endswith('</MENSAJES>'):
        xml_data += 'S>'
    root = ET.fromstring(xml_data)

    Fechas = []

    # Cargar XML existente
    if os.path.exists(XML_Mensajes):
        tree = ET.parse(XML_Mensajes)
        MENSAJES = tree.getroot()
    else:
        MENSAJES = ET.Element("MENSAJES")


    for mensaje in root.findall('MENSAJE'):
        fecha = mensaje.find('FECHA').text.strip()
        texto = mensaje.find('TEXTO').text.strip()
        texto = texto.lower()

        #abstraer la fecha de la forma de dd/mm/yyyy de la fecha
        patron_fecha = r'\d{2}/\d{2}/\d{4}'
        fechas = re.findall(patron_fecha, fecha)

        #Si no cumple esta parte enctonces se continua con la siguiente fecha
        if len(fechas) == 0:
            continue

        fecha = fechas[0]

        fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")
        fecha = fecha_obj.strftime("%d-%m-%Y")

        objMensaje = {
            'fecha': fecha,
            'texto': texto
        }


        LISTA_USR_MENCIONADOS_temp = []
        LISTA_HASH_INCLUIDOS_temp = []
        LISTA_Palabras_INCLUIDOS_temp = []

        analizador(texto, LISTA_USR_MENCIONADOS_temp, LISTA_HASH_INCLUIDOS_temp, LISTA_Palabras_INCLUIDOS_temp)

        Fechas.append(fechastem(fecha, LISTA_USR_MENCIONADOS_temp, LISTA_HASH_INCLUIDOS_temp))
  
        mensaje = ET.SubElement(MENSAJES, "MENSAJE")
        ET.SubElement(mensaje, "FECHA").text = objMensaje['fecha']
        ET.SubElement(mensaje, "TEXTO").text = objMensaje['texto']
        

    tree = ET.ElementTree(MENSAJES)
    tree.write(XML_Mensajes, encoding="utf-8") 


    elementos_procesados = set()

    FechasAgrupadas = []


    for i in range(len(Fechas)):
        fencha1 = Fechas[i]

        if fencha1 not in elementos_procesados:
            fecha = []
            NumeroMensajes = 1
            fencha11 = Fechas[i].fecha
            conjunto1_mensiones = set(Fechas[i].LISTA_USR_MENCIONADOS)
            conjunto1_hast = set(Fechas[i].LISTA_HASH_INCLUIDOS)

            for j in range(i + 1, len(Fechas)):
                fencha2 = Fechas[j]
                if fencha2 not in elementos_procesados:
                    fencha22 = Fechas[j].fecha
                    conjunto2_mensiones = set(Fechas[j].LISTA_USR_MENCIONADOS)
                    conjunto2_hast = set(Fechas[j].LISTA_HASH_INCLUIDOS)
                    if fencha11 == fencha22:
                        conjunto1_mensiones = conjunto1_mensiones | conjunto2_mensiones
                        conjunto1_hast = conjunto1_hast | conjunto2_hast
                        elementos_procesados.add(fencha2)
                        NumeroMensajes += 1

            listamesiones = list(conjunto1_mensiones)
            listaconjuntos = list(conjunto1_hast)

            fecha.append(str(fencha11))
            fecha.append(str(NumeroMensajes))
            fecha.append(str(len(listamesiones)))
            fecha.append(str(len(listaconjuntos)))
            FechasAgrupadas.append(fecha)
            elementos_procesados.add(fencha1)


    MENSAJES_RECIBIDOS = ET.Element("MENSAJES_RECIBIDOS")
    for elemento_data in FechasAgrupadas:
        tiempo = ET.SubElement(MENSAJES_RECIBIDOS, "TIEMPO")
        etiquetas = ["FECHA", "MSJ_RECIBIDOS", "USR_MENCIONADOS", "HASH_INCLUIDOS"]
        
        for etiqueta, valor in zip(etiquetas, elemento_data):
            etiqueta_elemento = ET.SubElement(tiempo, etiqueta)
            etiqueta_elemento.text = valor

    # Crear un objeto ElementTree a partir de la raíz
    tree = ET.ElementTree(MENSAJES_RECIBIDOS)

    # Generar el XML como una cadena
    xml_string = ET.tostring(MENSAJES_RECIBIDOS, encoding="utf-8").decode()


    # Parsear la cadena XML
    dom = xml.dom.minidom.parseString(xml_string)

    # Dar formato al XML
    formatted_xml = dom.toprettyxml()


    # Retornar el XML como una respuesta HTTP
    return Response(formatted_xml, content_type="application/xml; charset=utf-8")

def isCaracterValido(ascii):
    if 65 <= ascii <= 90 or 97 <= ascii <= 122:
        return True
    return False

     
def analizador(texto, LISTA_USR_MENCIONADOS_temp, LISTA_HASH_INCLUIDOS_temp, LISTA_Palabras_INCLUIDOS_temp):
    estado = 0
    estado_anterior = 0
    lexema = ""
    for caracter in texto:

        ascii = ord(caracter)

        if estado == 0:
            if ascii == 64:
                lexema += caracter
                estado = 1
                estado_anterior = 0
            elif ascii == 35:
                lexema += caracter
                estado = 2
                estado_anterior = 0
            elif ascii == 32:
                estado = 0
                estado_anterior = 0
                pass
            else:
                lexema += caracter
                estado = 3

        elif estado == 1:
            if caracter.isdigit() or isCaracterValido(ascii) or ascii == 95:
                lexema += caracter
                estado_anterior = 1
            else:
                estado = 4
                estado_anterior = 1


        elif estado == 2:
            if ascii != 35:
                lexema += caracter
                estado_anterior = 2
            else:
                lexema += caracter
                estado = 4
                estado_anterior = 2


        elif estado == 3:
            if ascii != 32:
                lexema += caracter
                estado_anterior = 3
            else:
                estado = 4
                estado_anterior = 3


        elif estado == 4:

            if estado_anterior == 1:
                LISTA_USR_MENCIONADOS_temp.append(lexema)            
            elif estado_anterior == 2:
                LISTA_HASH_INCLUIDOS_temp.append(lexema)
            elif estado_anterior == 3:
                LISTA_Palabras_INCLUIDOS_temp.append(lexema)

            lexema = ""
            if ascii == 64:
                lexema += caracter
                estado = 1
                estado_anterior = 0
            elif ascii == 35:
                lexema += caracter
                estado = 2
                estado_anterior = 0
            elif ascii == 32:
                estado = 0
                estado_anterior = 0
                pass
            else:
                lexema += caracter
                estado = 3
                estado_anterior = 0


    if estado != 0:
        if estado_anterior == 1:
            LISTA_USR_MENCIONADOS_temp.append(lexema)
        elif estado_anterior == 2:
            LISTA_HASH_INCLUIDOS_temp.append(lexema)
        elif estado_anterior == 3:
            LISTA_Palabras_INCLUIDOS_temp.append(lexema)


@app.route('/search-by-date-hashtags/<fecha>', methods=['GET'])
def search_by_hashtags(fecha):

    fechas = fecha.split("-")
    dia = fechas[2]
    mes = fechas[1]
    ano = fechas[0]
    fecha = f'{dia}-{mes}-{ano}'

    if not os.path.exists(XML_Mensajes):
        return None

    # Cargar XML existente

    tree = ET.parse(XML_Mensajes)
    MENSAJES = tree.getroot()

    list_Hashtags = []

    for data in tree.findall('MENSAJE'):
        fecha_bd = data.find('FECHA').text
        texto_bd = data.find('TEXTO').text
        if fecha == fecha_bd:
            LISTA_USR_MENCIONADOS_temp = []
            LISTA_HASH_INCLUIDOS_temp = []
            LISTA_Palabras_INCLUIDOS_temp = []
            analizador(texto_bd, LISTA_USR_MENCIONADOS_temp, LISTA_HASH_INCLUIDOS_temp, LISTA_Palabras_INCLUIDOS_temp)
            for hash in LISTA_HASH_INCLUIDOS_temp:
                list_Hashtags.append(hash)


    result_list = []
    elementos_procesados = set()

    for i in range(len(list_Hashtags)):
        no_hashtag = 1
        hashtag1 = list_Hashtags[i]
        if hashtag1 not in elementos_procesados:
            for j in range(i + 1, len(list_Hashtags)):
                hashtag2 = list_Hashtags[j]
                if hashtag2 not in elementos_procesados:
                    if hashtag1 == hashtag2:
                        no_hashtag += 1
                        elementos_procesados.add(hashtag2)
            elementos_procesados.add(hashtag1)

            obj = {
                'fecha': fecha,
                'hashtags': hashtag1,
                'numero': no_hashtag,
            }

            # Usamos el alias como clave
            result_list.append(obj)

    return jsonify(result_list)



@app.route('/search-by-date-mentions/<fecha>', methods=['GET'])
def search_by_mentions(fecha):
    fechas = fecha.split("-")
    dia = fechas[2]
    mes = fechas[1]
    ano = fechas[0]
    fecha = f'{dia}-{mes}-{ano}'

    if not os.path.exists(XML_Mensajes):
        return None

    # Cargar XML existente

    tree = ET.parse(XML_Mensajes)
    MENSAJES = tree.getroot()

    list_mensiones = []

    for data in tree.findall('MENSAJE'):
        fecha_bd = data.find('FECHA').text
        texto_bd = data.find('TEXTO').text
        if fecha == fecha_bd:
            LISTA_USR_MENCIONADOS_temp = []
            LISTA_HASH_INCLUIDOS_temp = []
            LISTA_Palabras_INCLUIDOS_temp = []
            analizador(texto_bd, LISTA_USR_MENCIONADOS_temp, LISTA_HASH_INCLUIDOS_temp, LISTA_Palabras_INCLUIDOS_temp)
            for user in LISTA_USR_MENCIONADOS_temp:
                list_mensiones.append(user)


    result_list = []
    elementos_procesados = set()

    for i in range(len(list_mensiones)):
        no_mensiones = 1
        mension1 = list_mensiones[i]
        if mension1 not in elementos_procesados:
            for j in range(i + 1, len(list_mensiones)):
                mension2 = list_mensiones[j]
                if mension2 not in elementos_procesados:
                    if mension1 == mension2:
                        no_mensiones += 1
                        elementos_procesados.add(mension2)
            elementos_procesados.add(mension1)

            obj = {
                'fecha': fecha,
                'mension': mension1,
                'numero': no_mensiones,
            }

            # Usamos el alias como clave
            result_list.append(obj)

    return jsonify(result_list)


@app.route('/search-by-date-feelings/<fecha>', methods=['GET'])
def search_by_feelings(fecha):
    if not os.path.exists(XML_Mensajes):
        return None
    return None


@app.route('/lista', methods=['GET'])
def search_by_vacio():
    if not os.path.exists(XML_Mensajes):
        return None
    return None

if __name__ == '__main__':
    app.run(debug=True)
