from tinydb import TinyDB, Query
from datetime import datetime

# Conectamos con tu archivo de ficheros
db = TinyDB('datos.json')

def registrar_alerta(nombre, casco, chaleco):
    """
    Esta función la llamaremos cuando David y Cris detecten algo.
    """
    estado = "Completo" if casco and chaleco else "INCOMPLETO"
    
    db.insert({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'empleado': nombre,
        'casco': casco,
        'chaleco': chaleco,
        'resultado': estado
    })
    return "Registro guardado"

# Prueba esto: Descomenta la línea de abajo para probar un guardado
registrar_alerta("German", True, False)