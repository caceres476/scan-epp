import boto3
import json
import os
import time
from datetime import datetime
from botocore.exceptions import ClientError
from pathlib import Path
from dotenv import load_dotenv
import winsound

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
NOMBRE_COLECCION = os.getenv("NOMBRE_COLECCION", "trabajadores_epp")

BASE_DIR = Path(__file__).resolve().parent
CARPETA_INCIDENTES = BASE_DIR / "imagenes_incidentes"
ARCHIVO_TRABAJADORES = BASE_DIR / "trabajadores.json"
ARCHIVO_INCIDENCIAS = BASE_DIR / "incidencias.json"
ARCHIVO_PROCESADAS = BASE_DIR / "procesadas.json"
ARCHIVO_ALERTAS = BASE_DIR / "alertas_pendientes.json"
ARCHIVO_DATOS_TRABAJADORES = BASE_DIR / "datos_trabajadores.json"

rekognition = boto3.client("rekognition", region_name=AWS_REGION)

def sonar_alerta():
    try:
        winsound.Beep(1500, 700)
        winsound.Beep(1500, 700)
    except Exception:
        print("\a")

def cargar_json(ruta, valor_default):
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
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

def obtener_tipos_incidencia(nombre_archivo):
    nombre = nombre_archivo.lower()
    tipos_detectados = []
    
    # Manejar variaciones
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
        
    if not tipos_detectados:
        tipos_detectados.append("Incidencia no especificada")
        
    return tipos_detectados

def obtener_datos_trabajador(face_id, external_id):
    trabajadores = cargar_json(ARCHIVO_TRABAJADORES, {})
    datos_trabajadores = cargar_json(ARCHIVO_DATOS_TRABAJADORES, {})

    codigo = "DESCONOCIDO"
    nombre = "Trabajador no identificado"
    area = "No disponible"
    puesto = "No disponible"

    # Buscar en trabajadores.json usando external_id o face_id si estuviera mapeado distinto
    if external_id in trabajadores:
        datos = trabajadores[external_id]
        codigo = datos.get("codigo", codigo)
        nombre = datos.get("nombre", nombre)
        area = datos.get("area", area)
        puesto = datos.get("puesto", puesto)
    elif face_id in trabajadores: # Compatibilidad
        datos = trabajadores[face_id]
        codigo = datos.get("codigo", codigo)
        nombre = datos.get("nombre", nombre)
        area = datos.get("area", area)
        puesto = datos.get("puesto", puesto)
    else:
        # Fallback a nombre de external_id
        if external_id and external_id != "desconocido":
            nombre = external_id.replace("_", " ").title()

    # Sobrescribir con info completa de datos_trabajadores si existe codigo
    if codigo in datos_trabajadores:
        completo = datos_trabajadores[codigo]
        nombre = completo.get("nombre", nombre)
        area = completo.get("area", area)
        puesto = completo.get("puesto", puesto)

    return codigo, nombre, area, puesto

def generar_alerta(incidencia):
    alertas = cargar_json(ARCHIVO_ALERTAS, [])
    
    # Copiar los datos de la incidencia a la alerta
    nueva_alerta = incidencia.copy()
    nueva_alerta["estado"] = "pendiente"
    
    alertas.append(nueva_alerta)
    guardar_json(ARCHIVO_ALERTAS, alertas)

    print("ALERTA GUARDADA EN alertas_pendientes.json")
    sonar_alerta()

def guardar_incidencia(codigo, nombre, area, puesto, tipos_incidencia, confianza, ruta_imagen_rel, estado="registrada"):
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
        "imagen": ruta_imagen_rel,
        "estado": estado
    }

    incidencias.append(nueva_incidencia)
    guardar_json(ARCHIVO_INCIDENCIAS, incidencias)
    return nueva_incidencia

def identificar_trabajador(ruta_imagen, tipos_incidencia):
    """
    Esta funcion realiza la evaluacion de rostro enviando la imagen a
    AWS Rekognition y buscando coincidencias en la coleccion.
    """
    if not CARPETA_INCIDENTES.exists():
        CARPETA_INCIDENTES.mkdir(parents=True, exist_ok=True)
        
    ruta_imagen_path = Path(ruta_imagen)
    ruta_relativa = f"imagenes_incidentes/{ruta_imagen_path.name}"
    
    # Esperar un poco a que el archivo termine de copiarse por completo
    time.sleep(1)

    try:
        with open(ruta_imagen, "rb") as imagen:
            bytes_imagen = imagen.read()
            if len(bytes_imagen) == 0:
                print("Imagen vacia:", ruta_imagen)
                return False
    except Exception as e:
        print("Error leyendo imagen:", e)
        return False

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
            # Guardar incidencia como desconocida
            incidencia = guardar_incidencia(
                "DESCONOCIDO", 
                "Trabajador no identificado", 
                "No disponible", 
                "No disponible", 
                tipos_incidencia, 
                0, 
                ruta_relativa,
                "no_identificado"
            )
            generar_alerta(incidencia)
            return True

        mejor_coincidencia = coincidencias[0]
        face_id = mejor_coincidencia["Face"]["FaceId"]
        external_id = mejor_coincidencia["Face"].get("ExternalImageId", "desconocido")
        confianza = round(mejor_coincidencia["Similarity"], 2)

        codigo, nombre, area, puesto = obtener_datos_trabajador(face_id, external_id)

        print("------------------------------------")
        print("Imagen procesada:", ruta_relativa)
        print("Trabajador identificado:", nombre)
        print("Incidencias:", ", ".join(tipos_incidencia))
        print("Confianza:", confianza, "%")

        incidencia = guardar_incidencia(codigo, nombre, area, puesto, tipos_incidencia, confianza, ruta_relativa)
        generar_alerta(incidencia)

        print("Incidencia guardada correctamente")

        return True

    except ClientError as error:
        codigo = error.response["Error"]["Code"]

        if codigo == "InvalidParameterException":
            print("No se pudo procesar la imagen. Puede que no haya rostro visible:", ruta_imagen)
            # Registrar incidencia no identificada
            incidencia = guardar_incidencia(
                "DESCONOCIDO", 
                "Trabajador no identificado", 
                "No disponible", 
                "No disponible", 
                tipos_incidencia, 
                0, 
                ruta_relativa,
                "no_identificado"
            )
            generar_alerta(incidencia)
            return True
        elif codigo == "ResourceNotFoundException":
            print("No existe la coleccion:", NOMBRE_COLECCION)
            return False
        else:
            print("Error con AWS Rekognition:")
            print(error)
            return False

def obtener_imagenes():
    """
    Escanea la carpeta de incidentes en busqueda de imagenes
    nuevas (jpg, jpeg, png) para su posterior analisis.
    """
    extensiones_validas = [".jpg", ".jpeg", ".png"]
    imagenes = []

    if not CARPETA_INCIDENTES.exists():
        CARPETA_INCIDENTES.mkdir(parents=True, exist_ok=True)

    for ruta_archivo in CARPETA_INCIDENTES.iterdir():
        if ruta_archivo.is_file() and ruta_archivo.suffix.lower() in extensiones_validas:
            imagenes.append(str(ruta_archivo))

    return imagenes

def monitorear_carpeta():
    """
    Ciclo principal que revisa continuamente la carpeta de imagenes
    e invoca la evaluacion de rostro por cada archivo nuevo detectado.
    """
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
                nombre_archivo = Path(ruta_imagen).name
                tipos_incidencia = obtener_tipos_incidencia(nombre_archivo)

                print("Nueva imagen detectada:", nombre_archivo)

                resultado = identificar_trabajador(ruta_imagen, tipos_incidencia)

                if resultado:
                    procesadas.append(ruta_normalizada)
                    guardar_json(ARCHIVO_PROCESADAS, procesadas)

        time.sleep(3)

if __name__ == "__main__":
    monitorear_carpeta()
