import boto3
import json
import os
from botocore.exceptions import ClientError

NOMBRE_COLECCION = "trabajadores_epp"
ARCHIVO_TRABAJADORES = "trabajadores.json"

rekognition = boto3.client("rekognition")


def cargar_trabajadores():
    if not os.path.exists(ARCHIVO_TRABAJADORES):
        return {}

    with open(ARCHIVO_TRABAJADORES, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_trabajadores(datos):
    with open(ARCHIVO_TRABAJADORES, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def registrar_trabajador(nombre, ruta_imagen):
    if not os.path.exists(ruta_imagen):
        print("No existe la imagen:", ruta_imagen)
        return

    with open(ruta_imagen, "rb") as imagen:
        bytes_imagen = imagen.read()

    try:
        respuesta = rekognition.index_faces(
            CollectionId=NOMBRE_COLECCION,
            Image={"Bytes": bytes_imagen},
            ExternalImageId=nombre,
            DetectionAttributes=["DEFAULT"],
            MaxFaces=1,
            QualityFilter="AUTO"
        )

        registros = respuesta.get("FaceRecords", [])

        if len(registros) == 0:
            print("No se detecto ningun rostro en la imagen.")
            return

        face_id = registros[0]["Face"]["FaceId"]

        trabajadores = cargar_trabajadores()
        trabajadores[face_id] = {
            "nombre": nombre,
            "imagen_registro": ruta_imagen
        }
        guardar_trabajadores(trabajadores)

        print("Trabajador registrado correctamente")
        print("Nombre:", nombre)
        print("FaceId:", face_id)

    except ClientError as error:
        print("Error al registrar trabajador:")
        print(error)


if __name__ == "__main__":
    nombre = input("Ingrese el nombre del trabajador: ").strip().lower()
    ruta = input("Ingrese la ruta de la imagen: ").strip()

    registrar_trabajador(nombre, ruta)