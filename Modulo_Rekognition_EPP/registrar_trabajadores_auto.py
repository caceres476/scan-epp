import boto3
import json
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from pathlib import Path
from datetime import datetime

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
NOMBRE_COLECCION = os.getenv("NOMBRE_COLECCION", "trabajadores_epp")

BASE_DIR = Path(__file__).resolve().parent
CARPETA_REGISTRO = BASE_DIR / "imagenes_registro"
ARCHIVO_TRABAJADORES = BASE_DIR / "trabajadores.json"
ARCHIVO_DATOS_TRABAJADORES = BASE_DIR / "datos_trabajadores.json"

rekognition = boto3.client("rekognition", region_name=AWS_REGION)

def cargar_json(ruta, valor_default):
    if not ruta.exists():
        return valor_default
    with open(ruta, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()
        if not contenido:
            return valor_default
        try:
            return json.loads(contenido)
        except json.JSONDecodeError:
            return valor_default

def guardar_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

def obtener_datos_desde_nombre_archivo(nombre_archivo):
    # Formato: TRA001_cris_reyes.jpg
    nombre_sin_extension = os.path.splitext(nombre_archivo)[0]
    partes = nombre_sin_extension.split("_")
    
    codigo = partes[0]
    nombre = " ".join(partes[1:]).title() if len(partes) > 1 else nombre_sin_extension
    external_id = nombre_sin_extension
    
    return codigo, nombre, external_id

def trabajador_ya_registrado(datos_trabajadores, external_id):
    for trabajador in datos_trabajadores.values():
        if trabajador.get("external_image_id") == external_id:
            return True
    return False

def registrar_imagen_en_aws(ruta_imagen, external_id):
    with open(ruta_imagen, "rb") as imagen:
        bytes_imagen = imagen.read()

    respuesta = rekognition.index_faces(
        CollectionId=NOMBRE_COLECCION,
        Image={"Bytes": bytes_imagen},
        ExternalImageId=external_id,
        DetectionAttributes=["DEFAULT"],
        MaxFaces=1,
        QualityFilter="AUTO"
    )

    registros = respuesta.get("FaceRecords", [])
    if len(registros) == 0:
        print(f"[ERROR] No se detecto rostro en: {ruta_imagen.name}")
        return None

    return registros[0]["Face"]["FaceId"]

def registrar_trabajadores_automaticamente():
    if not CARPETA_REGISTRO.exists():
        CARPETA_REGISTRO.mkdir(parents=True, exist_ok=True)

    trabajadores = cargar_json(ARCHIVO_TRABAJADORES, {})
    datos_trabajadores = cargar_json(ARCHIVO_DATOS_TRABAJADORES, {})

    extensiones_validas = [".jpg", ".jpeg", ".png"]

    print("====================================")
    print(" REGISTRO AUTOMATICO DE TRABAJADORES")
    print("====================================")

    archivos = [f for f in CARPETA_REGISTRO.iterdir() if f.is_file() and f.suffix.lower() in extensiones_validas]
    
    if not archivos:
        print("No se encontraron imagenes en la carpeta imagenes_registro.")
        return

    for ruta_imagen in archivos:
        archivo = ruta_imagen.name
        codigo, nombre, external_id = obtener_datos_desde_nombre_archivo(archivo)

        if external_id in trabajadores or trabajador_ya_registrado(datos_trabajadores, external_id):
            print(f"[INFO] Ya estaba registrado: {archivo}")
            continue

        print(f"\nProcesando nuevo trabajador: {archivo}")
        
        try:
            face_id = registrar_imagen_en_aws(ruta_imagen, external_id)

            if face_id is not None:
                print("Por favor complete los datos faltantes para este trabajador.")
                area = input(f"Area para {nombre} ({codigo}): ").strip() or "No disponible"
                puesto = input(f"Puesto para {nombre} ({codigo}): ").strip() or "No disponible"
                
                trabajadores[external_id] = {
                    "codigo": codigo,
                    "nombre": nombre,
                    "area": area,
                    "puesto": puesto,
                    "imagen": f"imagenes_registro/{archivo}"
                }

                datos_trabajadores[codigo] = {
                    "codigo": codigo,
                    "nombre": nombre,
                    "area": area,
                    "puesto": puesto,
                    "imagen": f"imagenes_registro/{archivo}",
                    "external_image_id": external_id,
                    "fecha_registro": datetime.now().strftime("%Y-%m-%d"),
                    "hora_registro": datetime.now().strftime("%H:%M:%S")
                }

                guardar_json(ARCHIVO_TRABAJADORES, trabajadores)
                guardar_json(ARCHIVO_DATOS_TRABAJADORES, datos_trabajadores)

                print("[OK] Trabajador registrado correctamente.")
                print("------------------------------------")

        except ClientError as error:
            print(f"[ERROR] AWS fallo al registrar: {archivo}")
            print(error)
            print("------------------------------------")

    print("\nProceso terminado.")

if __name__ == "__main__":
    registrar_trabajadores_automaticamente()
