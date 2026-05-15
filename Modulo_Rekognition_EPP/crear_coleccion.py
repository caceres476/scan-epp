import boto3
from botocore.exceptions import ClientError

NOMBRE_COLECCION = "trabajadores_epp"

rekognition = boto3.client("rekognition")

try:
    respuesta = rekognition.create_collection(
        CollectionId=NOMBRE_COLECCION
    )

    print("Coleccion creada correctamente")
    print("Nombre:", NOMBRE_COLECCION)
    print("ARN:", respuesta["CollectionArn"])
    print("StatusCode:", respuesta["StatusCode"])

except ClientError as error:
    codigo = error.response["Error"]["Code"]

    if codigo == "ResourceAlreadyExistsException":
        print("La coleccion ya existe:", NOMBRE_COLECCION)
    else:
        print("Error al crear la coleccion:")
        print(error)