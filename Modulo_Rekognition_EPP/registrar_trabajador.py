import boto3
import json
import os
import sys
import cv2
import shutil
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from pathlib import Path

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
NOMBRE_COLECCION = os.getenv("NOMBRE_COLECCION", "trabajadores_epp")

BASE_DIR = Path(__file__).resolve().parent
RUTA_REGISTRO = BASE_DIR / "imagenes_registro"
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

def formatear_nombre_archivo(codigo, nombre):
    nombre_limpio = nombre.lower().replace(" ", "_")
    return f"{codigo}_{nombre_limpio}"

def registrar_en_aws(ruta_imagen, external_id):
    with open(ruta_imagen, "rb") as imagen:
        bytes_imagen = imagen.read()

    try:
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
            print("[ERROR] No se detecto ningun rostro en la imagen.")
            return None
        return registros[0]["Face"]["FaceId"]
    except ClientError as error:
        print("[ERROR] AWS Rekognition fallo al registrar:")
        print(error)
        return None

def registrar_trabajador(modo):
    print("====================================")
    if modo == "camara":
        print(" REGISTRO CON CAMARA LOCAL")
    else:
        print(" REGISTRO DESDE IMAGEN EXISTENTE")
    print("====================================\n")

    codigo = input("Ingrese el codigo del trabajador (ej. TRA001): ").strip()
    nombre = input("Ingrese el nombre completo: ").strip()
    area = input("Ingrese el area: ").strip()
    puesto = input("Ingrese el puesto: ").strip()

    if not codigo or not nombre:
        print("[ERROR] El codigo y el nombre son obligatorios.")
        return

    nombre_archivo_base = formatear_nombre_archivo(codigo, nombre)
    ruta_destino = RUTA_REGISTRO / f"{nombre_archivo_base}.jpg"
    
    # Manejar duplicados de nombre de archivo
    contador = 1
    while ruta_destino.exists():
        ruta_destino = RUTA_REGISTRO / f"{nombre_archivo_base}_{contador}.jpg"
        contador += 1

    if modo == "camara":
        print("\nAbriendo camara...")
        print(" - Presione ESPACIO para capturar.")
        print(" - Presione ESC para cancelar.")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] No se pudo abrir la camara.")
            return

        capturado = False
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] No se pudo leer de la camara.")
                break
            
            cv2.imshow("Registro Trabajador - Presione ESPACIO para capturar, ESC para cancelar", frame)
            key = cv2.waitKey(1)
            
            if key == 32: # ESPACIO
                cv2.imwrite(str(ruta_destino), frame)
                print("\n[OK] Foto capturada y guardada.")
                capturado = True
                break
            elif key == 27: # ESC
                print("\nCaptura cancelada.")
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        if not capturado:
            return

    elif modo == "archivo":
        ruta_origen = input("Ingrese la ruta absoluta o relativa de la imagen existente: ").strip().strip('"').strip("'")
        ruta_origen_path = Path(ruta_origen)
        
        if not ruta_origen_path.exists() or not ruta_origen_path.is_file():
            print(f"[ERROR] No existe el archivo: {ruta_origen}")
            return
            
        try:
            shutil.copy(ruta_origen_path, ruta_destino)
            print("\n[OK] Imagen copiada correctamente a la carpeta de registro.")
        except Exception as e:
            print(f"[ERROR] No se pudo copiar la imagen: {e}")
            return

    print("\nRegistrando rostro en AWS Rekognition...")
    external_id = nombre_archivo_base
    face_id = registrar_en_aws(ruta_destino, external_id)

    if not face_id:
        print("[ERROR] No se pudo registrar el trabajador debido a que no se encontro un rostro valido.")
        if ruta_destino.exists():
            ruta_destino.unlink() # Borrar imagen no valida
        return

    # Guardar en trabajadores.json (para mapeo simple)
    trabajadores = cargar_json(ARCHIVO_TRABAJADORES, {})
    # Modificado para relacionar el ExternalImageId con los datos como pidio el usuario
    # El usuario pide: "El archivo trabajadores.json debe servir para relacionar el ExternalImageId de Rekognition con los datos del trabajador."
    trabajadores[external_id] = {
        "codigo": codigo,
        "nombre": nombre,
        "area": area,
        "puesto": puesto,
        "imagen": f"imagenes_registro/{ruta_destino.name}"
    }
    guardar_json(ARCHIVO_TRABAJADORES, trabajadores)

    # Guardar en datos_trabajadores.json (informacion completa)
    from datetime import datetime
    datos_trabajadores = cargar_json(ARCHIVO_DATOS_TRABAJADORES, {})
    datos_trabajadores[codigo] = {
        "codigo": codigo,
        "nombre": nombre,
        "area": area,
        "puesto": puesto,
        "imagen": f"imagenes_registro/{ruta_destino.name}",
        "external_image_id": external_id,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d"),
        "hora_registro": datetime.now().strftime("%H:%M:%S")
    }
    guardar_json(ARCHIVO_DATOS_TRABAJADORES, datos_trabajadores)

    print("\n[OK] Trabajador registrado exitosamente en el sistema.")
    print(f" - Codigo: {codigo}")
    print(f" - Nombre: {nombre}")
    print(f" - Imagen: {ruta_destino.name}")

if __name__ == "__main__":
    modo = "camara"
    if len(sys.argv) > 1:
        if sys.argv[1] == "archivo":
            modo = "archivo"
            
    registrar_trabajador(modo)