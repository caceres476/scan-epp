import boto3
import json
import os
import winsound
from datetime import datetime
from botocore.exceptions import ClientError
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
NOMBRE_COLECCION = os.getenv("NOMBRE_COLECCION", "trabajadores_epp")

BASE_DIR = Path(__file__).resolve().parent
ARCHIVO_TRABAJADORES = BASE_DIR / "trabajadores.json"
ARCHIVO_INCIDENCIAS = BASE_DIR / "incidencias.json"
ARCHIVO_ALERTAS = BASE_DIR / "alertas_pendientes.json"
ARCHIVO_DATOS_TRABAJADORES = BASE_DIR / "datos_trabajadores.json"

rekognition = boto3.client("rekognition", region_name=AWS_REGION)

def cargar_json(ruta, valor_default):
    """
    Lee y parsea un archivo JSON de forma segura, manejando casos
    en los que el archivo no existe o esta corrupto.
    """
    if not ruta.exists():
        return valor_default

    with open(ruta, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()
        if contenido == "":
            return valor_default
        try:
            return json.loads(contenido)
        except json.JSONDecodeError:
            return valor_default

def guardar_json(ruta, datos):
    """
    Guarda un diccionario o lista en un archivo JSON en disco,
    asegurando el formato y la codificacion correcta.
    """
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

def sonar_alerta():
    """
    Emite un pitido desde el sistema operativo para notificar
    visualmente (auditivamente) de una nueva incidencia detectada.
    """
    try:
        winsound.Beep(1500, 700)
        winsound.Beep(1500, 700)
    except Exception:
        print("\a")

def obtener_datos_trabajador(face_id, external_id):
    """
    Cruza el ID del rostro de AWS con la base de datos local JSON
    para extraer la informacion corporativa completa del trabajador.
    """
    trabajadores = cargar_json(ARCHIVO_TRABAJADORES, {})
    datos_trabajadores = cargar_json(ARCHIVO_DATOS_TRABAJADORES, {})

    codigo = "DESCONOCIDO"
    nombre = "Trabajador no identificado"
    area = "No disponible"
    puesto = "No disponible"

    if external_id in trabajadores:
        datos = trabajadores[external_id]
        codigo = datos.get("codigo", codigo)
        nombre = datos.get("nombre", nombre)
        area = datos.get("area", area)
        puesto = datos.get("puesto", puesto)
    elif face_id in trabajadores:
        datos = trabajadores[face_id]
        codigo = datos.get("codigo", codigo)
        nombre = datos.get("nombre", nombre)
        area = datos.get("area", area)
        puesto = datos.get("puesto", puesto)
    else:
        if external_id and external_id != "desconocido":
            nombre = external_id.replace("_", " ").title()

    if codigo in datos_trabajadores:
        completo = datos_trabajadores[codigo]
        nombre = completo.get("nombre", nombre)
        area = completo.get("area", area)
        puesto = completo.get("puesto", puesto)

    return codigo, nombre, area, puesto

def obtener_tipos_incidencia(nombre_archivo):
    """
    Analiza el nombre del archivo de imagen para deducir qué 
    equipos de protección personal (EPP) faltan en la escena.
    """
    nombre = nombre_archivo.lower()
    tipos_detectados = []
    
    if "sin_casco" in nombre or "sin casco" in nombre:
        tipos_detectados.append("Sin casco")
    if "sin_guantes" in nombre or "sin guantes" in nombre:
        tipos_detectados.append("Sin guantes")
    if "sin_lentes" in nombre or "sin lentes" in nombre:
        tipos_detectados.append("Sin lentes")
    if "sin_chaleco" in nombre or "sin chaleco" in nombre:
        tipos_detectados.append("Sin chaleco")
    if "sin_mascarilla" in nombre or "sin mascarilla" in nombre:
        tipos_detectados.append("Sin mascarilla")
        
    return tipos_detectados

def guardar_incidencia(codigo, nombre, area, puesto, tipos_incidencia, confianza, ruta_imagen, estado="registrada"):
    """
    Registra el evento de incumplimiento en el historial principal de incidencias.
    Genera la fecha y hora oficial en este preciso momento.
    """
    incidencias = cargar_json(ARCHIVO_INCIDENCIAS, [])
    
    ahora = datetime.now()

    nueva_incidencia = {
        "id": len(incidencias) + 1,
        "codigo_trabajador": codigo,
        "nombre": nombre,
        "area": area,
        "puesto": puesto,
        "tipos_incidencia": tipos_incidencia,
        "tipo_incidencia": ", ".join(tipos_incidencia),
        "fecha": ahora.strftime("%Y-%m-%d"),
        "hora": ahora.strftime("%H:%M:%S"),
        "confianza_rekognition": confianza,
        "imagen": ruta_imagen.replace("\\", "/"),
        "estado": estado
    }

    incidencias.append(nueva_incidencia)
    guardar_json(ARCHIVO_INCIDENCIAS, incidencias)
    print("Incidencia guardada correctamente")
    return nueva_incidencia

def generar_alerta(incidencia):
    """
    Copia una incidencia recien registrada a la bandeja de pendientes,
    para que posteriormente pueda ser revisada manualmente.
    """
    alertas = cargar_json(ARCHIVO_ALERTAS, [])
    
    nueva_alerta = incidencia.copy()
    nueva_alerta["estado"] = "pendiente"

    alertas.append(nueva_alerta)
    guardar_json(ARCHIVO_ALERTAS, alertas)
    sonar_alerta()
    print("ALERTA GENERADA: Nueva incidencia detectada")

def identificar_trabajador_manual(ruta_imagen, tipos_entrada):
    """
    Esta funcion realiza la evaluacion de rostro enviando la imagen a
    AWS Rekognition y buscando coincidencias en la coleccion.
    """
    ruta_path = Path(ruta_imagen)
    if not ruta_path.exists():
        print("No existe la imagen:", ruta_imagen)
        return

    # Si no nos dan tipos, tratar de obtenerlos del nombre
    tipos_incidencia = []
    if tipos_entrada:
        tipos_incidencia = [t.strip() for t in tipos_entrada.split(",")]
    else:
        tipos_incidencia = obtener_tipos_incidencia(ruta_path.name)
        
    if not tipos_incidencia:
        tipos_incidencia.append("Incidencia no especificada")

    trabajadores = cargar_json(ARCHIVO_TRABAJADORES, {})
    if len(trabajadores) == 0:
        print("No hay trabajadores registrados. Continuando busqueda de rostros de todas formas...")

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
            incidencia = guardar_incidencia("DESCONOCIDO", "Trabajador no identificado", "No disponible", "No disponible", tipos_incidencia, 0, ruta_imagen, "no_identificado")
            generar_alerta(incidencia)
            return

        mejor_coincidencia = coincidencias[0]
        face_id = mejor_coincidencia["Face"]["FaceId"]
        external_id = mejor_coincidencia["Face"].get("ExternalImageId", "desconocido")
        confianza = round(mejor_coincidencia["Similarity"], 2)

        codigo, nombre, area, puesto = obtener_datos_trabajador(face_id, external_id)

        print("------------------------------------")
        print("Trabajador identificado:", nombre)
        print("Codigo:", codigo)
        print("Incidencia:", ", ".join(tipos_incidencia))
        print("Confianza:", confianza, "%")
        print("Imagen:", ruta_imagen)
        print("------------------------------------")

        incidencia = guardar_incidencia(codigo, nombre, area, puesto, tipos_incidencia, confianza, ruta_imagen)
        generar_alerta(incidencia)

    except ClientError as error:
        codigo = error.response["Error"]["Code"]
        if codigo == "InvalidParameterException":
            print("No se pudo procesar la imagen. Puede que no haya rostro visible.")
            incidencia = guardar_incidencia("DESCONOCIDO", "Trabajador no identificado", "No disponible", "No disponible", tipos_incidencia, 0, ruta_imagen, "no_identificado")
            generar_alerta(incidencia)
        elif codigo == "ResourceNotFoundException":
            print("No existe la coleccion:", NOMBRE_COLECCION)
        else:
            print("Error al identificar trabajador:")
            print(error)

if __name__ == "__main__":
    ruta = input("Ingrese la ruta de la imagen del incidente: ").strip()
    incidencia_txt = input("Ingrese el tipo de incidencia (separado por comas, o deje vacio para auto-detectar): ").strip()

    identificar_trabajador_manual(ruta, incidencia_txt)