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
        trabajador = incidencia.get("trabajador", "desconocido")
        tipo = incidencia.get("tipo_incidencia", "incidencia de EPP")

        reporte[trabajador][tipo] += 1
        totales[trabajador] += 1

    print("====================================")
    print("REPORTE GENERAL DE INCIDENCIAS")
    print("====================================")

    for trabajador, tipos in reporte.items():
        print()
        print("Trabajador:", trabajador)
        print("Total de incidencias:", totales[trabajador])

        for tipo, cantidad in tipos.items():
            print("-", tipo + ":", cantidad)

    print()
    print("====================================")
    print("Total general de incidencias:", len(incidencias))
    print("====================================")


if __name__ == "__main__":
    generar_reporte()