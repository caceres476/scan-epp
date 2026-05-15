import boto3
import json
import os
import time
from datetime import datetime
from botocore.exceptions import ClientError
import winsound

NOMBRE_COLECCION = "trabajadores_epp"

CARPETA_INCIDENTES = "imagenes_incidentes"
ARCHIVO_TRABAJADORES = "trabajadores.json"
ARCHIVO_INCIDENCIAS = "incidencias.json"
ARCHIVO_PROCESADAS = "procesadas.json"
ARCHIVO_ALERTAS = "alertas_pendientes.json"

rekognition = boto3.client("rekognition")

def sonar_alerta():
    try:
        winsound.Beep(1500, 700)
        winsound.Beep(1500, 700)
    except Exception:
        print("\a")

def cargar_json(ruta, valor_default):
    if not os.path.exists(ruta):
        return valor_default

    with open(ruta, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()

        if contenido == "":
            return valor_default

        return json.loads(contenido)


def guardar_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def obtener_tipo_incidencia(nombre_archivo):
    nombre = nombre_archivo.lower()

    if "sin_casco" in nombre:
        return "sin casco"
    elif "sin_guantes" in nombre:
        return "sin guantes"
    elif "sin_lentes" in nombre:
        return "sin lentes"
    elif "sin_chaleco" in nombre:
        return "sin chaleco"
    else:
        return "incidencia de EPP"
    
def generar_alerta(incidencia):
    alertas = cargar_json(ARCHIVO_ALERTAS, [])

    nueva_alerta = {
        "nombre": incidencia["nombre"],
        "area": incidencia["area"],
        "puesto": incidencia["puesto"],
        "tipo_incidencia": incidencia["tipo_incidencia"],
        "fecha": incidencia["fecha"],
        "hora": incidencia["hora"],
        "confianza_rekognition": incidencia["confianza_rekognition"],
        "imagen": incidencia["imagen"],
        "estado": "pendiente"
    }

    alertas.append(nueva_alerta)
    guardar_json(ARCHIVO_ALERTAS, alertas)

    print("ALERTA GUARDADA EN alertas_pendientes.json")
    sonar_alerta()


def guardar_incidencia(nombre, tipo_incidencia, confianza, ruta_imagen):
    incidencias = cargar_json(ARCHIVO_INCIDENCIAS, [])

    nueva_incidencia = {
        "id": len(incidencias) + 1,
        "trabajador": nombre,
        "tipo_incidencia": tipo_incidencia,
        "confianza": confianza,
        "imagen": ruta_imagen.replace("\\", "/"),
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S")
    }

    incidencias.append(nueva_incidencia)
    guardar_json(ARCHIVO_INCIDENCIAS, incidencias)


def identificar_trabajador(ruta_imagen, tipo_incidencia):
    trabajadores = cargar_json(ARCHIVO_TRABAJADORES, {})

    if len(trabajadores) == 0:
        print("No hay trabajadores registrados.")
        return False

    with open(ruta_imagen, "rb") as imagen:
        bytes_imagen = imagen.read()

    try:
        respuesta = rekognition.search_faces_by_image(
            CollectionId=NOMBRE_COLECCION,
            Image={"Bytes": bytes_imagen},
            FaceMatchThreshold=80,
            MaxFaces=1,
            QualityFilter="AUTO"
        )

        coincidencias = respuesta.get("FaceMatches", [])

        if len(coincidencias) == 0:
            print("No se encontro coincidencia para:", ruta_imagen)
            return True

        mejor_coincidencia = coincidencias[0]
        face_id = mejor_coincidencia["Face"]["FaceId"]
        confianza = round(mejor_coincidencia["Similarity"], 2)

        if face_id in trabajadores:
            nombre = trabajadores[face_id]["nombre"]
        else:
            nombre = mejor_coincidencia["Face"].get("ExternalImageId", "desconocido")

        print("------------------------------------")
        print("Imagen procesada:", ruta_imagen.replace("\\", "/"))
        print("Trabajador identificado:", nombre)
        print("Incidencia:", tipo_incidencia)
        print("Confianza:", confianza, "%")

        guardar_incidencia(nombre, tipo_incidencia, confianza, ruta_imagen)

        print("Incidencia guardada correctamente")

        return True

    except ClientError as error:
        codigo = error.response["Error"]["Code"]

        if codigo == "InvalidParameterException":
            print("No se pudo procesar la imagen. Puede que no haya rostro visible:", ruta_imagen)
            return True
        elif codigo == "ResourceNotFoundException":
            print("No existe la coleccion:", NOMBRE_COLECCION)
            return False
        else:
            print("Error con AWS Rekognition:")
            print(error)
            return False


def obtener_imagenes():
    extensiones_validas = [".jpg", ".jpeg", ".png"]
    imagenes = []

    if not os.path.exists(CARPETA_INCIDENTES):
        os.makedirs(CARPETA_INCIDENTES)

    for archivo in os.listdir(CARPETA_INCIDENTES):
        ruta_completa = os.path.join(CARPETA_INCIDENTES, archivo)

        if os.path.isfile(ruta_completa):
            extension = os.path.splitext(archivo)[1].lower()

            if extension in extensiones_validas:
                imagenes.append(ruta_completa)

    return imagenes


def monitorear_carpeta():
    print("Monitor automatico iniciado...")
    print("Revisando carpeta:", CARPETA_INCIDENTES)
    print("Presiona CTRL + C para detener.")
    print("------------------------------------")

    while True:
        procesadas = cargar_json(ARCHIVO_PROCESADAS, [])
        imagenes = obtener_imagenes()

        for ruta_imagen in imagenes:
            ruta_normalizada = ruta_imagen.replace("\\", "/")

            if ruta_normalizada not in procesadas:
                nombre_archivo = os.path.basename(ruta_imagen)
                tipo_incidencia = obtener_tipo_incidencia(nombre_archivo)

                print("Nueva imagen detectada:", ruta_normalizada)

                resultado = identificar_trabajador(ruta_imagen, tipo_incidencia)

                if resultado:
                    procesadas.append(ruta_normalizada)
                    guardar_json(ARCHIVO_PROCESADAS, procesadas)

        time.sleep(3)


if __name__ == "__main__":
    monitorear_carpeta()
