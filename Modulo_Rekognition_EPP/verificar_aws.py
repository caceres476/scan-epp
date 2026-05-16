import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
NOMBRE_COLECCION = os.getenv("NOMBRE_COLECCION", "trabajadores_epp")

def verificar_aws():
    print("Verificando conexion con AWS Rekognition...")
    try:
        rekognition = boto3.client("rekognition", region_name=AWS_REGION)
        respuesta = rekognition.list_collections()
        colecciones = respuesta.get("CollectionIds", [])
        
        print("[OK] Conexion con AWS exitosa.")
        print("Colecciones disponibles:")
        if not colecciones:
            print(" - Ninguna coleccion encontrada.")
        else:
            for col in colecciones:
                print(f" - {col}")
                
        if NOMBRE_COLECCION in colecciones:
            print(f"\n[OK] La coleccion configurada '{NOMBRE_COLECCION}' existe.")
        else:
            print(f"\n[AVISO] La coleccion configurada '{NOMBRE_COLECCION}' NO existe.")
            print("Deberas crearla desde el menu principal.")
            
    except ClientError as error:
        print("\n[ERROR] Falla al conectar con AWS Rekognition:")
        codigo = error.response.get("Error", {}).get("Code", "Desconocido")
        print(f"Codigo de error: {codigo}")
        print("Causas posibles:")
        print(" - Credenciales invalidas en el archivo .env")
        print(" - Region incorrecta")
        print(" - Usuario AWS sin permisos suficientes")
    except Exception as e:
        print(f"\n[ERROR] Ocurrio un problema inesperado: {e}")
        print("Asegurate de que tienes conexion a internet y boto3 esta instalado.")

if __name__ == "__main__":
    verificar_aws()
