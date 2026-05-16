"""
Prueba de Comunicación Serial - Arduino
Plataforma: Windows
"""

import serial
import time

PUERTO = "COM3"  # Ajusta según tu Arduino
BAUDIOS = 9600

print("\n" + "=" * 60)
print("  PRUEBA DE COMUNICACIÓN SERIAL - ARDUINO")
print("  Plataforma: Windows")
print("=" * 60)
print(f"\n📡 Puerto: {PUERTO}")
print(f"📊 Baudios: {BAUDIOS}")

try:
    print("\n⏳ Conectando...")
    ser = serial.Serial(PUERTO, BAUDIOS, timeout=1)
    time.sleep(2)
    print(f"✅ Conectado exitosamente\n")
    
    # Prueba 1
    print("📤 Prueba 1: OK")
    ser.write(b"OK\n")
    time.sleep(1)
    print("   ✓ Verifica: LED verde encendido\n")
    
    # Prueba 2
    print("📤 Prueba 2: FALTA: Casco")
    ser.write(b"FALTA: Casco\n")
    time.sleep(4)
    print("   ✓ Verifica: LED rojo, buzzer, LCD\n")
    
    # Prueba 3
    print("📤 Prueba 3: FALTA: Casco, Chaleco")
    ser.write(b"FALTA: Casco, Chaleco\n")
    time.sleep(4)
    print("   ✓ Verifica: LCD muestra ambos items\n")
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("=" * 60)
    
except serial.SerialException as e:
    print(f"\n❌ ERROR SERIAL: {e}")
    print("\n💡 Soluciones para Windows:")
    print("   1. Abre Administrador de Dispositivos")
    print("   2. Expande 'Puertos (COM y LPT)'")
    print("   3. Busca 'Arduino Mega (COMx)'")
    print("   4. Actualiza PUERTO en el código")
    print("   5. Cierra el IDE de Arduino")

except Exception as e:
    print(f"\n❌ ERROR: {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("\n🔌 Puerto cerrado")