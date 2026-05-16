import json
import os
from collections import defaultdict

ARCHIVO_INCIDENCIAS = "incidencias.json"


def cargar_incidencias():
    if not os.path.exists(ARCHIVO_INCIDENCIAS):
        return []

    with open(ARCHIVO_INCIDENCIAS, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()

        if contenido == "":
            return []

        return json.loads(contenido)


def generar_reporte():
    incidencias = cargar_incidencias()

    if len(incidencias) == 0:
        print("No hay incidencias registradas.")
        return

    reporte = defaultdict(lambda: defaultdict(int))
    totales = defaultdict(int)

    for incidencia in incidencias:
        trabajador = incidencia.get("nombre", "Trabajador no identificado")
        codigo = incidencia.get("codigo_trabajador", "DESCONOCIDO")
        
        key_reporte = f"{codigo} - {trabajador}"
        
        # Soportar multiples incidencias (lista) o un string
        tipos = incidencia.get("tipos_incidencia", [])
        if not tipos:
            tipo_str = incidencia.get("tipo_incidencia", "Incidencia no especificada")
            if tipo_str:
                tipos = [t.strip() for t in tipo_str.split(",")]
        
        for tipo in tipos:
            reporte[key_reporte][tipo] += 1
            totales[key_reporte] += 1

    print("====================================")
    print("REPORTE GENERAL DE INCIDENCIAS")
    print("====================================")

    for trabajador, tipos_inc in reporte.items():
        print()
        print("Trabajador:", trabajador)
        print("Total de incidencias:", totales[trabajador])

        for tipo, cantidad in tipos_inc.items():
            print("-", tipo + ":", cantidad)

    print()
    print("====================================")
    print("Total general de incidencias:", len(incidencias))
    print("====================================")


if __name__ == "__main__":
    generar_reporte()