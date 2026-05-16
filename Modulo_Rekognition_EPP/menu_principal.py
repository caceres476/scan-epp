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

    # Usar el python del entorno virtual
    python_exe = "python"
    if os.path.exists("venv\\Scripts\\python.exe"):
        python_exe = "venv\\Scripts\\python.exe"

    monitor_proceso = subprocess.Popen(
        [python_exe, "monitor_carpeta.py"],
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

def crear_verificar_coleccion():
    print("Verificando/Creando coleccion de AWS Rekognition...\n")
    python_exe = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else "python"
    subprocess.run([python_exe, "crear_coleccion.py"])

def submenu_registrar_trabajador():
    python_exe = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else "python"
    while True:
        limpiar_pantalla()
        print("====================================")
        print(" REGISTRO DE TRABAJADOR")
        print("====================================")
        print("1. Registrar trabajador con camara local")
        print("2. Registrar trabajador desde imagen existente")
        print("3. Volver al menu principal")
        print("====================================")
        
        opcion = input("Seleccione una opcion: ").strip()
        limpiar_pantalla()
        
        if opcion == "1":
            subprocess.run([python_exe, "registrar_trabajador.py", "camara"])
            pausar()
        elif opcion == "2":
            subprocess.run([python_exe, "registrar_trabajador.py", "archivo"])
            pausar()
        elif opcion == "3":
            break
        else:
            print("Opcion no valida.")
            pausar()

def registrar_trabajadores_automaticamente():
    print("Ejecutando registro automatico de trabajadores...\n")
    python_exe = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else "python"
    subprocess.run([python_exe, "registrar_trabajadores_auto.py"])

def identificar_manualmente():
    print("Identificacion manual...\n")
    python_exe = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else "python"
    subprocess.run([python_exe, "identificar_trabajador.py"])

def verificar_configuracion():
    print("Verificando configuracion...\n")
    if os.path.exists("verificar_configuracion.bat"):
        subprocess.run(["verificar_configuracion.bat"])
    else:
        print("No se encontro verificar_configuracion.bat")

def generar_reporte():
    print("Generando reporte de incidencias...\n")
    python_exe = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else "python"
    subprocess.run([python_exe, "reporte_incidencias.py"])

def cargar_json_seguro(archivo, valor_default):
    if not os.path.exists(archivo):
        return valor_default

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        if contenido == "":
            return valor_default
        try:
            return json.loads(contenido)
        except json.JSONDecodeError:
            return valor_default

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
        print("Trabajador:", incidencia.get("nombre"))
        print("Codigo:", incidencia.get("codigo_trabajador"))
        print("Tipo:", incidencia.get("tipo_incidencia"))
        print("Confianza:", str(incidencia.get("confianza_rekognition")) + "%")
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
        print("Trabajador:", alerta.get("nombre"))
        print("Codigo:", alerta.get("codigo_trabajador"))
        print("Incidencia:", alerta.get("tipo_incidencia"))
        print("Confianza:", str(alerta.get("confianza_rekognition")) + "%")
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
    print("1. Crear o verificar coleccion de AWS Rekognition")
    print("2. Registrar trabajador")
    print("3. Registrar trabajadores automaticamente desde carpeta imagenes_registro")
    print("4. Iniciar monitor de carpeta imagenes_incidentes")
    print("5. Identificar trabajador en una imagen manualmente")
    print("6. Ver incidencias guardadas")
    print("7. Ver alertas pendientes")
    print("8. Generar reporte de incidencias")
    print("9. Verificar configuracion")
    print("10. Salir")
    print("====================================")

def main():
    global monitor_proceso

    while True:
        limpiar_pantalla()
        mostrar_menu()

        opcion = input("Seleccione una opcion: ").strip()

        limpiar_pantalla()

        if opcion == "1":
            crear_verificar_coleccion()
            pausar()
        elif opcion == "2":
            submenu_registrar_trabajador()
        elif opcion == "3":
            registrar_trabajadores_automaticamente()
            pausar()
        elif opcion == "4":
            iniciar_monitor()
            pausar()
        elif opcion == "5":
            identificar_manualmente()
            pausar()
        elif opcion == "6":
            ver_incidencias()
            pausar()
        elif opcion == "7":
            ver_alertas_pendientes()
            pausar()
        elif opcion == "8":
            generar_reporte()
            pausar()
        elif opcion == "9":
            verificar_configuracion()
            pausar()
        elif opcion == "10":
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