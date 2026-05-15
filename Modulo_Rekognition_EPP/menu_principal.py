import subprocess
import os
import json
import time

monitor_proceso = None


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\nPresione ENTER para continuar...")


def iniciar_monitor():
    global monitor_proceso

    if monitor_proceso is not None and monitor_proceso.poll() is None:
        print("El monitor automatico ya esta iniciado.")
        return

    monitor_proceso = subprocess.Popen(
        ["py", "monitor_carpeta.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    print("Monitor automatico iniciado en una ventana aparte.")
    print("Ahora el sistema revisara la carpeta imagenes_incidentes.")


def detener_monitor():
    global monitor_proceso

    if monitor_proceso is None or monitor_proceso.poll() is not None:
        print("El monitor automatico no esta activo.")
        return

    monitor_proceso.terminate()
    monitor_proceso = None

    print("Monitor automatico detenido correctamente.")


def registrar_empleados():
    print("Ejecutando registro automatico de empleados...\n")
    subprocess.run(["py", "registrar_empleados_auto.py"])


def generar_reporte():
    print("Generando reporte de incidencias...\n")
    subprocess.run(["py", "reporte_incidencias.py"])


def cargar_json_seguro(archivo, valor_default):
    if not os.path.exists(archivo):
        return valor_default

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read().strip()

        if contenido == "":
            return valor_default

        return json.loads(contenido)


def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


def ver_incidencias():
    archivo = "incidencias.json"

    incidencias = cargar_json_seguro(archivo, [])

    if len(incidencias) == 0:
        print("No hay incidencias registradas.")
        return

    print("====================================")
    print("INCIDENCIAS GUARDADAS")
    print("====================================")

    for incidencia in incidencias:
        print("ID:", incidencia.get("id"))
        print("Trabajador:", incidencia.get("trabajador"))
        print("Tipo:", incidencia.get("tipo_incidencia"))
        print("Confianza:", str(incidencia.get("confianza")) + "%")
        print("Imagen:", incidencia.get("imagen"))
        print("Fecha:", incidencia.get("fecha"))
        print("Hora:", incidencia.get("hora"))
        print("------------------------------------")


def contar_alertas_pendientes():
    archivo = "alertas_pendientes.json"
    alertas = cargar_json_seguro(archivo, [])
    return len(alertas)


def ver_alertas_pendientes():
    archivo = "alertas_pendientes.json"

    alertas = cargar_json_seguro(archivo, [])

    if len(alertas) == 0:
        print("No hay alertas pendientes.")
        return

    print("====================================")
    print(" ALERTAS PENDIENTES")
    print("====================================")

    for alerta in alertas:
        print("Trabajador:", alerta.get("trabajador"))
        print("Incidencia:", alerta.get("tipo_incidencia"))
        print("Confianza:", str(alerta.get("confianza")) + "%")
        print("Imagen:", alerta.get("imagen"))
        print("Fecha:", alerta.get("fecha"))
        print("Hora:", alerta.get("hora"))
        print("Estado:", alerta.get("estado"))
        print("------------------------------------")

    limpiar = input("Desea limpiar las alertas pendientes? s/n: ").strip().lower()

    if limpiar == "s":
        guardar_json(archivo, [])
        print("Alertas pendientes limpiadas correctamente.")


def mostrar_estado_monitor():
    if monitor_proceso is not None and monitor_proceso.poll() is None:
        print("Estado del monitor: ACTIVO")
    else:
        print("Estado del monitor: INACTIVO")


def mostrar_menu():
    alertas = contar_alertas_pendientes()

    print("====================================")
    print(" SISTEMA DE RECONOCIMIENTO FACIAL EPP")
    print("====================================")

    mostrar_estado_monitor()

    if alertas > 0:
        print("AVISO: Hay", alertas, "alerta(s) pendiente(s)")

    print("====================================")
    print("1. Iniciar monitor automatico")
    print("2. Registrar empleados automaticamente")
    print("3. Generar reporte de incidencias")
    print("4. Ver incidencias guardadas")
    print("5. Detener monitor automatico")
    print("6. Ver alertas pendientes")
    print("7. Salir")
    print("====================================")


def main():
    global monitor_proceso

    while True:
        limpiar_pantalla()
        mostrar_menu()

        opcion = input("Seleccione una opcion: ").strip()

        limpiar_pantalla()

        if opcion == "1":
            iniciar_monitor()
            pausar()

        elif opcion == "2":
            registrar_empleados()
            pausar()

        elif opcion == "3":
            generar_reporte()
            pausar()

        elif opcion == "4":
            ver_incidencias()
            pausar()

        elif opcion == "5":
            detener_monitor()
            pausar()

        elif opcion == "6":
            ver_alertas_pendientes()
            pausar()

        elif opcion == "7":
            if monitor_proceso is not None and monitor_proceso.poll() is None:
                detener_monitor()

            print("Saliendo del sistema...")
            time.sleep(1)
            break

        else:
            print("Opcion no valida.")
            pausar()


if __name__ == "__main__":
    main()