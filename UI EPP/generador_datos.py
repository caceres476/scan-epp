import json
import random
from datetime import datetime, timedelta

# Listas para simular variedad
nombres = ["Cris Reyes", "Carlos carlitos", "German Hernandez", "David Lopez", "Maria Garcia", "Juan Perez"]
areas = ["Torno", "Fresadora", "Logística", "Ensamble", "Fundición"]
incidencias = ["Sin casco", "Sin chaleco", "EPP Incompleto"]
puestos = ["Operario", "Supervisor", "Técnico"]

def generar_mes_datos():
    datos_simulados = []
    # Fecha inicial: 1 de abril de 2026
    fecha_inicio = datetime(2026, 4, 1)
    
    # Generamos datos para 30 días
    for i in range(30):
        fecha_actual = fecha_inicio + timedelta(days=i)
        
        # Generamos entre 2 y 6 incidencias por día para que sea realista
        for _ in range(random.randint(2, 6)):
            registro = {
                "id_empleado": f"EMP00{random.randint(1, 9)}",
                "nombre": random.choice(nombres),
                "area": random.choice(areas),
                "puesto": random.choice(puestos),
                "tipo_incidencia": random.choice(incidencias),
                "fecha": fecha_actual.strftime("%Y-%m-%d"),
                "hora": f"{random.randint(7, 18):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}",
                "confianza_rekognition": round(random.uniform(85.0, 100.0), 2)
            }
            datos_simulados.append(registro)
    
    # Guardamos todo en tu datos.json (esto borrará lo anterior y pondrá lo nuevo)
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(datos_simulados, f, indent=4)
    
    print(f"¡Éxito! Se han generado {len(datos_simulados)} registros para el mes de abril.")

if __name__ == "__main__":
    generar_mes_datos()