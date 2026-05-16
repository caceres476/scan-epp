"""
Sistema de Detección de EPP en Tiempo Real
Integración: YOLO11 + OpenCV + Arduino Serial
Plataforma: Windows
Modelo: SCAN_EPP/runs/detect/train2/weights/best.pt
"""

import cv2
import serial
import time
import sys
import os
from ultralytics import YOLO

# === CONFIGURACIÓN ===
PUERTO_SERIAL = "COM3"  # Windows: COM3, COM4, etc.
BAUDIOS = 9600

# Rutas absolutas para Windows
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN_EPP_ROOT = os.path.join(os.path.dirname(PROJECT_ROOT), "SCAN_EPP")

# Ruta al modelo entrenado
MODELO_PATH = os.path.join(SCAN_EPP_ROOT, "runs", "detect", "train2", "weights", "best.pt")

# Verificar que el modelo existe
if not os.path.exists(MODELO_PATH):
    print(f"❌ ERROR: Modelo no encontrado en:\n{MODELO_PATH}")
    print("\n💡 Verifica:")
    print(f"   1. Que SCAN_EPP exista en: {SCAN_EPP_ROOT}")
    print("   2. Que el archivo best.pt exista en runs/detect/train2/weights/")
    print("\n📂 Estructura esperada:")
    print("   /")
    print("   ├── Proyecto_EPP/")
    print("   └── SCAN_EPP/")
    print("       └── runs/detect/train2/weights/best.pt")
    sys.exit(1)

print(f"✅ Modelo encontrado: {MODELO_PATH}")

# Parámetros de detección
UMBRAL_CONF = 0.7
COOLDOWN_SEGUNDOS = 2.0
REQUERIDOS = ["Hard_hat", "Vest"]  # EPP obligatorio

def cargar_modelo():
    """Carga el modelo YOLO entrenado"""
    print(f"📦 Cargando modelo YOLO11...")
    return YOLO(MODELO_PATH)

def conectar_serial():
    """Conecta con Arduino por puerto serial"""
    try:
        ser = serial.Serial(PUERTO_SERIAL, BAUDIOS, timeout=1)
        time.sleep(2)  # Espera reset de Arduino
        print(f"✅ Arduino conectado en {PUERTO_SERIAL}")
        return ser
    except serial.SerialException as e:
        print(f"⚠️  No se pudo conectar a {PUERTO_SERIAL}: {e}")
        print("\n💡 Soluciones:")
        print("   1. Abre Administrador de Dispositivos → Puertos (COM y LPT)")
        print("   2. Verifica el número de puerto COM del Arduino")
        print("   3. Cierra el IDE de Arduino si está abierto")
        print("   4. Actualiza PUERTO_SERIAL en el código")
        return None

def boxes_overlap(box1, box2, iou_threshold=0.3):
    """Calcula si dos bounding boxes se superponen (IoU)"""
    x1, y1, x2, y2 = box1
    x3, y3, x4, y4 = box2
    xi1, yi1 = max(x1, x3), max(y1, y3)
    xi2, yi2 = min(x2, x4), min(y2, y4)
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x4 - x3) * (y4 - y3)
    union_area = box1_area + box2_area - inter_area
    return (inter_area / union_area) > iou_threshold if union_area > 0 else False

def main():
    # Inicialización
    print("\n" + "=" * 70)
    print("  SISTEMA DE MONITOREO DE EPP - AREA DE TORNO")
    print("  Plataforma: Windows | Arduino Mega 2560")
    print("=" * 70)
    
    # Cargar modelo
    model = cargar_modelo()
    print(f"📋 Clases disponibles: {len(model.names)}")
    
    # Conectar Arduino
    ser = conectar_serial()
    
    # Abrir cámara web
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ ERROR: No se pudo abrir la cámara web")
        print("💡 Verifica que la cámara esté conectada y no esté en uso")
        sys.exit(1)
    
    print(f"\n🎯 Configuración:")
    print(f"   - Umbral de confianza: {UMBRAL_CONF}")
    print(f"   - EPP requerido: {', '.join(REQUERIDOS)}")
    print(f"   - Cooldown entre alertas: {COOLDOWN_SEGUNDOS}s")
    print("\n🎮 Controles:")
    print("   - Presiona 'q' para salir")
    print("   - Las alertas se envían automáticamente al Arduino")
    print("\n" + "-" * 70 + "\n")
    
    ultima_alerta = 0.0
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error al leer frame de la cámara")
                break
            
            frame_count += 1
            
            # Inferencia YOLO (cada 3 frames para mejorar rendimiento)
            if frame_count % 3 == 0:
                results = model(frame, conf=UMBRAL_CONF, verbose=False)
                boxes = results[0].boxes
            else:
                boxes = None
            
            violacion = False
            falta = []
            
            if boxes is not None and len(boxes) > 0:
                # Separar detecciones por clase
                personas = [b for b in boxes if model.names[int(b.cls[0])] == "Person"]
                epp_detectado = {
                    "Hard_hat": [b for b in boxes if model.names[int(b.cls[0])] == "Hard_hat"],
                    "Vest": [b for b in boxes if model.names[int(b.cls[0])] == "Vest"],
                }
                
                # Verificar cada persona
                for p in personas:
                    p_box = p.xyxy[0].cpu().numpy()
                    falta_persona = []
                    
                    for epp in REQUERIDOS:
                        asociado = any(
                            boxes_overlap(p_box, epp_box.xyxy[0].cpu().numpy())
                            for epp_box in epp_detectado[epp]
                        )
                        if not asociado:
                            falta_persona.append(epp)
                    
                    if falta_persona:
                        violacion = True
                        falta = falta_persona
                        x1, y1, x2, y2 = map(int, p_box)
                        
                        # Dibujar rectángulo y texto de alerta
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        cv2.putText(frame, f"FALTA: {', '.join(falta_persona)}", 
                                   (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Enviar alerta al Arduino
            if violacion and ser and ser.is_open:
                ahora = time.time()
                if ahora - ultima_alerta > COOLDOWN_SEGUNDOS:
                    # Traducir a español para LCD
                    traduccion = {"Hard_hat": "Casco", "Vest": "Chaleco"}
                    items_es = [traduccion.get(item, item) for item in falta]
                    mensaje = f"FALTA: {', '.join(items_es)}"
                    
                    # Truncar si es muy largo (máx 30 chars)
                    if len(mensaje) > 30:
                        mensaje = mensaje[:27] + "..."
                    
                    ser.write((mensaje + "\n").encode('utf-8'))
                    ultima_alerta = ahora
                    timestamp = time.strftime('%H:%M:%S')
                    print(f"📡 [{timestamp}] {mensaje}")
            
            # Calcular FPS
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Mostrar información en pantalla
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            estado_texto = "ALERTA" if violacion else "OK"
            estado_color = (0, 0, 255) if violacion else (0, 255, 0)
            cv2.putText(frame, f"Estado: {estado_texto}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, estado_color, 2)
            
            # Mostrar frame
            cv2.imshow("Monitoreo EPP - Area de Torno", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n\n🛑 Detenido por usuario (Ctrl+C)")
    
    finally:
        # Limpieza
        cap.release()
        cv2.destroyAllWindows()
        if ser and ser.is_open:
            ser.close()
            print("🔌 Puerto serial cerrado")
        print("\n✅ Sistema detenido correctamente")

if __name__ == "__main__":
    main()