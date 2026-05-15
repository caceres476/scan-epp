import boto3
import json
import os
from botocore.exceptions import ClientError

NOMBRE_COLECCION = "trabajadores_epp"
CARPETA_REGISTRO = "imagenes_registro"
ARCHIVO_TRABAJADORES = "trabajadores.json"
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


def obtener_nombre_desde_archivo(nombre_archivo):
    nombre_sin_extension = os.path.splitext(nombre_archivo)[0]
    partes = nombre_sin_extension.split("_")

    if len(partes) >= 2:
        nombre = "_".join(partes[1:])
    else:
        nombre = nombre_sin_extension

    return nombre.lower()


def rostro_ya_registrado(trabajadores, ruta_imagen):
    for datos in trabajadores.values():
        if datos.get("imagen_registro") == ruta_imagen:
            return True

    return False


def registrar_imagen_en_aws(ruta_imagen, nombre_trabajador):
    with open(ruta_imagen, "rb") as imagen:
        bytes_imagen = imagen.read()

    respuesta = rekognition.index_faces(
        CollectionId=NOMBRE_COLECCION,
        Image={"Bytes": bytes_imagen},
        ExternalImageId=nombre_trabajador,
        DetectionAttributes=["DEFAULT"],
        MaxFaces=1,
        QualityFilter="AUTO"
    )

    registros = respuesta.get("FaceRecords", [])

    if len(registros) == 0:
        print("No se detecto rostro en:", ruta_imagen)
        return None

    face_id = registros[0]["Face"]["FaceId"]
    return face_id


def pedir_datos_empleado(nombre_sistema):
    print()
    print("Nuevo empleado detectado:", nombre_sistema)
    print("Ingrese los datos del empleado")
    print("------------------------------------")

    nombre_completo = input("Nombre completo: ").strip()
    area = input("Area: ").strip()
    puesto = input("Puesto: ").strip()

    if nombre_completo == "":
        nombre_completo = nombre_sistema.replace("_", " ").title()

    if area == "":
        area = "No especificada"

    if puesto == "":
        puesto = "No especificado"

    return {
        "nombre_completo": nombre_completo,
        "area": area,
        "puesto": puesto
    }


def registrar_empleados_automaticamente():
    if not os.path.exists(CARPETA_REGISTRO):
        os.makedirs(CARPETA_REGISTRO)

    trabajadores = cargar_json(ARCHIVO_TRABAJADORES, {})
    datos_empleados = cargar_json(ARCHIVO_DATOS_EMPLEADOS, {})

    extensiones_validas = [".jpg", ".jpeg", ".png"]

    print("====================================")
    print(" REGISTRO AUTOMATICO DE EMPLEADOS")
    print("====================================")

    for archivo in os.listdir(CARPETA_REGISTRO):
        extension = os.path.splitext(archivo)[1].lower()

        if extension not in extensiones_validas:
            continue

        ruta_imagen = os.path.join(CARPETA_REGISTRO, archivo).replace("\\", "/")

        if rostro_ya_registrado(trabajadores, ruta_imagen):
            print("Ya estaba registrado:", archivo)
            continue

        nombre_trabajador = obtener_nombre_desde_archivo(archivo)

        try:
            face_id = registrar_imagen_en_aws(ruta_imagen, nombre_trabajador)

            if face_id is not None:
                trabajadores[face_id] = {
                    "nombre": nombre_trabajador,
                    "imagen_registro": ruta_imagen
                }

                if nombre_trabajador not in datos_empleados:
                    datos_empleados[nombre_trabajador] = pedir_datos_empleado(nombre_trabajador)

                guardar_json(ARCHIVO_TRABAJADORES, trabajadores)
                guardar_json(ARCHIVO_DATOS_EMPLEADOS, datos_empleados)

                print()
                print("Empleado registrado correctamente")
                print("Nombre sistema:", nombre_trabajador)
                print("Nombre completo:", datos_empleados[nombre_trabajador]["nombre_completo"])
                print("Area:", datos_empleados[nombre_trabajador]["area"])
                print("Puesto:", datos_empleados[nombre_trabajador]["puesto"])
                print("Imagen:", ruta_imagen)
                print("FaceId:", face_id)
                print("------------------------------------")

        except ClientError as error:
            print("Error al registrar:", archivo)
            print(error)
            print("------------------------------------")

    print("Proceso terminado.")


if __name__ == "__main__":
    registrar_empleados_automaticamente()