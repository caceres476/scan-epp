import streamlit as st
import pandas as pd
import json
import os
import cv2
import time
import io
import pathlib
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# CONFIGURACIÓN BASE
# ═══════════════════════════════════════════════════════════

st.set_page_config(
    page_title="EPP SCANNER",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = pathlib.Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

MODEL_PATH = ROOT_DIR / "SCAN_EPP" / "runs" / "detect" / "train2" / "weights" / "best.pt"
SAVE_DIR = ROOT_DIR / "SCAN_EPP" / "runs" / "detect" / "demo"
DATA_PATH = BASE_DIR / "datos.json"

SAVE_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap');

.stApp {
    background: #070b11;
    color: #c9d8e8;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding: 1.5rem 2rem 2rem 2rem !important;
    max-width: 100% !important;
}

h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
}

.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 28px;
    background: #0c1420;
    border: 1px solid #1a2d45;
    border-radius: 10px;
    margin-bottom: 22px;
}

.nav-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 4px;
}

.nav-sub {
    font-size: 0.65rem;
    color: #4a6a8a;
    letter-spacing: 2px;
    margin-top: 3px;
}

.pill {
    padding: 5px 14px;
    border-radius: 20px;
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 1.5px;
    font-weight: 700;
}

.pill-on {
    background: rgba(0,255,128,0.1);
    border: 1px solid #00ff80;
    color: #00ff80;
}

.pill-off {
    background: rgba(255,60,60,0.1);
    border: 1px solid #ff3c3c;
    color: #ff3c3c;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 22px;
}

.mc {
    background: #0c1420;
    border: 1px solid #1a2d45;
    border-radius: 10px;
    padding: 20px;
    position: relative;
    overflow: hidden;
}

.mc::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
}

.mc-b::before { background: linear-gradient(90deg,#0066ff,#00c8ff); }
.mc-r::before { background: linear-gradient(90deg,#ff1744,#ff6d83); }
.mc-g::before { background: linear-gradient(90deg,#00c853,#69ff90); }
.mc-y::before { background: linear-gradient(90deg,#ffb300,#ffe57f); }

.mc-lbl {
    font-size: 0.6rem;
    color: #3a5a7a;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.mc-val {
    font-family: 'Orbitron', monospace;
    font-size: 1.9rem;
    font-weight: 900;
    color: #ffffff;
}

.mc-sub {
    font-size: 0.65rem;
    color: #2a4a6a;
    margin-top: 6px;
}

.panel {
    background: #0c1420;
    border: 1px solid #1a2d45;
    border-radius: 10px;
    padding: 18px;
}

.p-hdr {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.p-ttl {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    color: #6a8aaa;
    letter-spacing: 3px;
}

.badge-live {
    font-size: .6rem;
    padding: 3px 10px;
    border-radius: 10px;
    background: rgba(255,50,50,.15);
    border: 1px solid #ff3c3c;
    color: #ff3c3c;
    letter-spacing: 1px;
}

.badge-std {
    font-size: .6rem;
    padding: 3px 10px;
    border-radius: 10px;
    background: rgba(60,60,60,.2);
    border: 1px solid #333;
    color: #777;
    letter-spacing: 1px;
}

.feed-off {
    background: #060a10;
    border: 1px dashed #192a3a;
    border-radius: 8px;
    height: 420px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.fo-ico {
    font-size: 3rem;
    opacity: .15;
}

.fo-ttl {
    font-family: 'Orbitron', monospace;
    font-size: .72rem;
    color: #1e3a5a;
    letter-spacing: 3px;
}

.fo-hint {
    font-size: .62rem;
    color: #152535;
    letter-spacing: 1px;
}

div[data-testid="stButton"] > button {
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    font-size: .78rem !important;
    border-radius: 8px !important;
    height: 46px !important;
    width: 100% !important;
}

.sbar {
    display: flex;
    align-items: center;
    gap: 18px;
    flex-wrap: wrap;
    padding: 8px 14px;
    background: #060a10;
    border: 1px solid #192a3a;
    border-radius: 6px;
    margin-top: 10px;
}

.si {
    font-family: 'Orbitron', monospace;
    font-size: .6rem;
    color: #3a5a7a;
    letter-spacing: 1.5px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.dot-g {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #00c853;
    box-shadow: 0 0 7px #00c853;
}

.dot-r {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #ff3c3c;
}

.si-val {
    color: #00c8ff;
}

.bbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 20px;
    background: #0c1420;
    border: 1px solid #1a2d45;
    border-radius: 10px;
}

.bbar-txt {
    font-size: .65rem;
    color: #2a4a6a;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════

valores_iniciales = {
    "cam_on": False,
    "cap": None,
    "t0": time.time(),
    "fps": 0.0,
    "conf_val": 0.70,
    "last_save": 0,
}

for k, v in valores_iniciales.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════
# FUNCIONES
# ═══════════════════════════════════════════════════════════

def cargar_datos():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@st.cache_resource
def cargar_modelo():
    from ultralytics import YOLO

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No se encontró el modelo en: {MODEL_PATH}")

    return YOLO(str(MODEL_PATH))


def abrir_camara():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        cap.release()
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    return cap


def cerrar_camara():
    st.session_state.cam_on = False

    if st.session_state.cap is not None:
        st.session_state.cap.release()
        st.session_state.cap = None


def analizar_incumplimientos(results):
    clases_detectadas = []

    if results[0].boxes is None:
        return []

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        nombre_clase = results[0].names[cls_id]
        clases_detectadas.append(nombre_clase)

    hay_persona_o_epp = any(
        clase in clases_detectadas
        for clase in ["Person", "Hard_hat", "Vest", "Mask", "Gloves"]
    )

    if not hay_persona_o_epp:
        return []

    incumplimientos = []

    if "Hard_hat" not in clases_detectadas:
        incumplimientos.append("Sin casco")

    if "Vest" not in clases_detectadas:
        incumplimientos.append("Sin chaleco")

    if "Mask" not in clases_detectadas:
        incumplimientos.append("Sin mascarilla")

    if "Gloves" not in clases_detectadas:
        incumplimientos.append("Sin guantes")

    return incumplimientos


def guardar_captura_si_aplica(frame, results):
    incumplimientos = analizar_incumplimientos(results)

    if not incumplimientos:
        return

    ahora = time.time()

    if ahora - st.session_state.last_save >= 5:
        texto_incumplimiento = "_".join(incumplimientos).replace(" ", "_")

        nombre_archivo = SAVE_DIR / f"incidencia_{texto_incumplimiento}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

        cv2.imwrite(str(nombre_archivo), frame)

        st.session_state.last_save = ahora


@st.cache_data
def convertir_excel(datos):
    buffer = io.BytesIO()

    df_excel = pd.DataFrame(datos)

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_excel.to_excel(
            writer,
            index=False,
            sheet_name="EPP_Reporte"
        )

    return buffer.getvalue()
        

# ═══════════════════════════════════════════════════════════
# DATOS
# ═══════════════════════════════════════════════════════════

datos = cargar_datos()
df = pd.DataFrame(datos) if datos else pd.DataFrame()

# ═══════════════════════════════════════════════════════════
# NAVBAR
# ═══════════════════════════════════════════════════════════

pill = '<span class="pill pill-on">● ACTIVA</span>' if st.session_state.cam_on else '<span class="pill pill-off">○ OFFLINE</span>'
nowstr = datetime.now().strftime("%H:%M:%S")
datestr = datetime.now().strftime("%d/%m/%Y")

st.markdown(f"""
<div class="navbar">
  <div>
    <div class="nav-title">🦺 EPP SCANNER</div>
    <div class="nav-sub">SISTEMA DE DETECCIÓN · TALLER DE TORNO · YOLO</div>
  </div>
  <div style="display:flex; align-items:center; gap:18px;">
    {pill}
    <div style="font-family:Orbitron; font-size:.7rem; color:#3a5a7a; letter-spacing:2px;">
      {datestr} · {nowstr}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# MÉTRICAS
# ═══════════════════════════════════════════════════════════

total = len(df) if not df.empty else 0
hoy = datetime.now().strftime("%Y-%m-%d")
alertas_hoy = len(df[df["fecha"] == hoy]) if not df.empty and "fecha" in df.columns else 0
conf_prom = f"{int(df['confianza_rekognition'].mean())}%" if not df.empty and "confianza_rekognition" in df.columns else "—"
area_critica = df["area"].mode()[0] if not df.empty and "area" in df.columns else "—"

st.markdown(f"""
<div class="metric-grid">
  <div class="mc mc-b">
    <div class="mc-lbl">Total Incidencias</div>
    <div class="mc-val">{total}</div>
    <div class="mc-sub">Historial completo</div>
  </div>
  <div class="mc mc-r">
    <div class="mc-lbl">Alertas Hoy</div>
    <div class="mc-val">{alertas_hoy}</div>
    <div class="mc-sub">Eventos del día</div>
  </div>
  <div class="mc mc-g">
    <div class="mc-lbl">Confianza IA</div>
    <div class="mc-val">{conf_prom}</div>
    <div class="mc-sub">Promedio registrado</div>
  </div>
  <div class="mc mc-y">
    <div class="mc-lbl">Área Crítica</div>
    <div class="mc-val" style="font-size:1.05rem;padding-top:8px">{area_critica}</div>
    <div class="mc-sub">Mayor recurrencia</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# CUERPO PRINCIPAL
# ═══════════════════════════════════════════════════════════

col_cam, col_tbl = st.columns([1.65, 1], gap="medium")

with col_cam:
    live_badge = '<span class="badge-live">● REC</span>' if st.session_state.cam_on else '<span class="badge-std">STANDBY</span>'

    st.markdown(f"""
    <div class="panel" style="padding-bottom:10px">
      <div class="p-hdr">
        <div class="p-ttl">📡 MONITOREO EN VIVO</div>
        {live_badge}
      </div>
    </div>
    """, unsafe_allow_html=True)

    b1, b2 = st.columns([1, 2])

    with b1:
        if not st.session_state.cam_on:
            if st.button("▶ ENCENDER", type="primary"):
                try:
                    cargar_modelo()
                    cap = abrir_camara()

                    if cap is None:
                        st.error("❌ No se pudo abrir la cámara en source=0.")
                    else:
                        st.session_state.cap = cap
                        st.session_state.cam_on = True
                        st.session_state.t0 = time.time()
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al iniciar: {e}")
        else:
            if st.button("■ APAGAR"):
                cerrar_camara()
                st.rerun()

    with b2:
        st.session_state.conf_val = st.slider(
            "Confianza mínima",
            0.30,
            0.95,
            st.session_state.conf_val,
            0.05,
            format="%.2f",
        )

    frame_slot = st.empty()
    sbar_slot = st.empty()

    if not st.session_state.cam_on:
        frame_slot.markdown("""
        <div class="feed-off">
          <div class="fo-ico">📷</div>
          <div class="fo-ttl">FEED DESACTIVADO</div>
          <div class="fo-hint">Presiona ENCENDER para iniciar detección</div>
        </div>
        """, unsafe_allow_html=True)

        sbar_slot.markdown("""
        <div class="sbar">
          <div class="si"><div class="dot-r"></div>MODELO: STANDBY</div>
          <div class="si">YOLO · EPP: CASCO · CHALECO · PERSONA</div>
          <div class="si">SOURCE: CAM 0</div>
        </div>
        """, unsafe_allow_html=True)

with col_tbl:
    st.markdown("""
    <div class="panel" style="padding-bottom:10px">
      <div class="p-hdr">
        <div class="p-ttl">📋 ÚLTIMAS INCIDENCIAS</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not df.empty:
        columnas = [c for c in ["nombre", "tipo_incidencia", "hora", "area"] if c in df.columns]

        st.dataframe(
            df[columnas].tail(14).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            height=440,
        )
    else:
        st.info("Sin registros aún.")

# ═══════════════════════════════════════════════════════════
# LOOP DE CÁMARA ESTABLE
# ═══════════════════════════════════════════════════════════

def camera_loop():
    if not st.session_state.cam_on:
        return

    cap = st.session_state.cap

    if cap is None or not cap.isOpened():
        cerrar_camara()
        return

    model = cargar_modelo()

    while st.session_state.cam_on:
        ret, frame = cap.read()

        if not ret:
            st.warning("❌ No se pudo leer la cámara.")
            break

        frame = cv2.resize(frame, (640, 480))

        results = model.predict(
            source=frame,
            conf=st.session_state.conf_val,
            verbose=False,
            imgsz=416
        )

        annotated_frame = results[0].plot()

        detecciones = (
            len(results[0].boxes)
            if results[0].boxes is not None
            else 0
        )

        guardar_captura_si_aplica(
            annotated_frame,
            results
        )

        tiempo_actual = time.time()

        fps_actual = 1.0 / max(
            tiempo_actual - st.session_state.t0,
            1e-6
        )

        st.session_state.fps = (
            fps_actual * 0.20 +
            st.session_state.fps * 0.80
        )

        st.session_state.t0 = tiempo_actual

        rgb = cv2.cvtColor(
            annotated_frame,
            cv2.COLOR_BGR2RGB
        )

        frame_slot.image(
            rgb,
            channels="RGB",
            use_container_width=True
        )

        sbar_slot.markdown(f"""
        <div class="sbar">
          <div class="si"><div class="dot-g"></div>MODELO: ACTIVO</div>
          <div class="si">FPS <span class="si-val">{st.session_state.fps:.1f}</span></div>
          <div class="si">DETECCIONES <span class="si-val">{detecciones}</span></div>
          <div class="si">CONF <span class="si-val">{st.session_state.conf_val:.2f}</span></div>
          <div class="si">RES <span class="si-val">640x480</span></div>
          <div class="si">IMG <span class="si-val">416</span></div>
          <div class="si">{datetime.now().strftime('%H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.01)

    cerrar_camara()

if st.session_state.cam_on:
    camera_loop()

# ═══════════════════════════════════════════════════════════
# GRÁFICAS
# ═══════════════════════════════════════════════════════════

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

if not df.empty:
    gc1, gc2 = st.columns(2, gap="medium")

    with gc1:
        st.markdown('<div class="panel"><div class="p-ttl" style="margin-bottom:14px">📊 INCIDENCIAS POR EMPLEADO</div>', unsafe_allow_html=True)
        if "nombre" in df.columns:
            st.bar_chart(df["nombre"].value_counts(), height=220, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with gc2:
        st.markdown('<div class="panel"><div class="p-ttl" style="margin-bottom:14px">📈 INCIDENCIAS POR ÁREA</div>', unsafe_allow_html=True)
        if "area" in df.columns:
            st.bar_chart(df["area"].value_counts(), height=220, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# BARRA FINAL
# ═══════════════════════════════════════════════════════════

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

bc1, bc2, bc3 = st.columns([1, 1, 3])

with bc1:
    if not df.empty:
        st.download_button(
            "📥 Descargar Excel",
            data=convertir_excel(datos),
            file_name=f"EPP_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


with bc3:
    st.markdown(f"""
    <div class="bbar">
      <span class="bbar-txt">EPP SCANNER v2.1 · YOLO · Taller de Torno</span>
      <span class="bbar-txt">{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)