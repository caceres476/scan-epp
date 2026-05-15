import boto3
import json
import os
import winsound
from datetime import datetime
from botocore.exceptions import ClientError

NOMBRE_COLECCION = "trabajadores_epp"
ARCHIVO_TRABAJADORES = "trabajadores.json"
ARCHIVO_INCIDENCIAS = "incidencias.json"
ARCHIVO_ALERTAS = "alertas_pendientes.json"
ARCHIVO_DATOS_EMPLEADOS = "datos_empleados.json"

rekognition = boto3.client("rekognition")


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


def sonar_alerta():
    try:
        winsound.Beep(1500, 700)
        winsound.Beep(1500, 700)
    except Exception:
        print("\a")

def obtener_datos_empleado(nombre_sistema):
    datos_empleados = cargar_json(ARCHIVO_DATOS_EMPLEADOS, {})

    if nombre_sistema in datos_empleados:
        return datos_empleados[nombre_sistema]

    return {
        "nombre_completo": nombre_sistema.replace("_", " ").title(),
        "area": "No especificada",
        "puesto": "No especificado"
    }

def guardar_incidencia(nombre_sistema, tipo_incidencia, confianza, ruta_imagen):
    incidencias = cargar_json(ARCHIVO_INCIDENCIAS, [])
    datos_empleado = obtener_datos_empleado(nombre_sistema)

    nueva_incidencia = {
        "nombre": datos_empleado.get("nombre_completo", nombre_sistema),
        "area": datos_empleado.get("area", "No especificada"),
        "puesto": datos_empleado.get("puesto", "No especificado"),
        "tipo_incidencia": tipo_incidencia,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S"),
        "confianza_rekognition": confianza,
        "imagen": ruta_imagen.replace("\\", "/")
    }

    incidencias.append(nueva_incidencia)
    guardar_json(ARCHIVO_INCIDENCIAS, incidencias)

    print("Incidencia guardada correctamente")

    return nueva_incidencia


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
        "imagen": incidencia["imagen"]
    }

    alertas.append(nueva_alerta)
    guardar_json(ARCHIVO_ALERTAS, alertas)

    sonar_alerta()

    print("ALERTA GENERADA: Nueva incidencia detectada")


def identificar_trabajador(ruta_imagen, tipo_incidencia):
    if not os.path.exists(ruta_imagen):
        print("No existe la imagen:", ruta_imagen)
        return

    trabajadores = cargar_json(ARCHIVO_TRABAJADORES, {})

    if len(trabajadores) == 0:
        print("No hay trabajadores registrados.")
        return

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
            print("No se encontro coincidencia con ningun trabajador registrado.")
            return

        mejor_coincidencia = coincidencias[0]
        face_id = mejor_coincidencia["Face"]["FaceId"]
        confianza = round(mejor_coincidencia["Similarity"], 2)

        if face_id in trabajadores:
            nombre = trabajadores[face_id]["nombre"]
        else:
            nombre = mejor_coincidencia["Face"].get("ExternalImageId", "desconocido")

        print("------------------------------------")
        print("Trabajador identificado:", nombre)
        print("Incidencia:", tipo_incidencia)
        print("Confianza:", confianza, "%")
        print("Imagen:", ruta_imagen.replace("\\", "/"))
        print("------------------------------------")

        incidencia = guardar_incidencia(
            nombre,
            tipo_incidencia,
            confianza,
            ruta_imagen
        )

        generar_alerta(incidencia)

    except ClientError as error:
        codigo = error.response["Error"]["Code"]

        if codigo == "InvalidParameterException":
            print("No se pudo procesar la imagen. Puede que no haya rostro visible.")
        elif codigo == "ResourceNotFoundException":
            print("No existe la coleccion:", NOMBRE_COLECCION)
        else:
            print("Error al identificar trabajador:")
            print(error)


if __name__ == "__main__":
    ruta = input("Ingrese la ruta de la imagen del incidente: ").strip()
    incidencia = input("Ingrese el tipo de incidencia: ").strip()

    identificar_trabajador(ruta, incidencia)