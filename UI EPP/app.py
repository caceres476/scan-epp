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

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

/* =========================================================
   BASE
========================================================= */

.stApp{
    background:#030712;
    color:#dbeafe;
}

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
}

#MainMenu,
footer,
header{
    visibility:hidden;
}

.block-container{
    padding-top:0.8rem !important;
    padding-bottom:0.8rem !important;
    padding-left:1rem !important;
    padding-right:1rem !important;
    max-width:100% !important;
}

/* =========================================================
   NAVBAR
========================================================= */

.navbar{
    display:flex;
    justify-content:space-between;
    align-items:center;

    padding:18px 24px;

    background:
    linear-gradient(
        135deg,
        #0b1120 0%,
        #0f172a 50%,
        #111827 100%
    );

    border:1px solid #1e293b;
    border-radius:16px;

    margin-bottom:14px;

    box-shadow:
    0 0 18px rgba(0,229,255,.08);
}

.nav-left{
    display:flex;
    flex-direction:column;
    gap:4px;
}

.nav-title{
    font-family:'Orbitron',monospace;
    font-size:1.45rem;
    font-weight:900;
    letter-spacing:3px;
    color:#ffffff;
}

.nav-sub{
    font-size:.62rem;
    color:#4f78a3;
    letter-spacing:2px;
}

.nav-right{
    display:flex;
    align-items:center;
    gap:14px;
}

.pill{
    padding:6px 16px;
    border-radius:20px;

    font-family:'Orbitron',monospace;
    font-size:.62rem;
    font-weight:700;
    letter-spacing:1px;
}

.pill-on{
    background:rgba(0,255,157,.10);
    border:1px solid #00ff9d;
    color:#00ff9d;
}

.pill-off{
    background:rgba(255,59,92,.10);
    border:1px solid #ff3b5c;
    color:#ff3b5c;
}

.nav-time{
    font-size:.65rem;
    color:#64748b;
    letter-spacing:1px;
}

/* =========================================================
   MÉTRICAS
========================================================= */

.metric-grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:12px;
    margin-bottom:14px;
}

.mc{
    position:relative;

    background:
    linear-gradient(
        145deg,
        #0b1120,
        #0d1726
    );

    border:1px solid #1e293b;
    border-radius:16px;

    padding:14px;

    min-height:95px;

    overflow:hidden;

    transition:.25s ease;

    box-shadow:
    0 0 15px rgba(0,229,255,.05);
}

.mc:hover{
    transform:translateY(-3px);

    border-color:#00e5ff;

    box-shadow:
    0 0 24px rgba(0,229,255,.14);
}

.mc::before{
    content:'';

    position:absolute;

    top:0;
    left:0;
    right:0;

    height:3px;
}

.mc-b::before{
    background:
    linear-gradient(
        90deg,
        #2563eb,
        #00e5ff
    );
}

.mc-r::before{
    background:
    linear-gradient(
        90deg,
        #ff1744,
        #ff6b81
    );
}

.mc-g::before{
    background:
    linear-gradient(
        90deg,
        #00c853,
        #00ff9d
    );
}

.mc-y::before{
    background:
    linear-gradient(
        90deg,
        #ffb300,
        #ffe082
    );
}

.mc-lbl{
    font-size:.55rem;
    text-transform:uppercase;
    letter-spacing:2px;
    color:#4f78a3;

    margin-bottom:10px;
}

.mc-val{
    font-family:'Orbitron',monospace;
    font-size:1.55rem;
    font-weight:900;
    color:#ffffff;
}

.mc-sub{
    margin-top:6px;

    font-size:.62rem;
    color:#3d5c7a;
}

/* =========================================================
   PANELES
========================================================= */

.panel{
    background:
    linear-gradient(
        145deg,
        #0b1120,
        #0d1726
    );

    border:1px solid #1e293b;
    border-radius:16px;

    padding:14px;

    box-shadow:
    0 0 20px rgba(0,229,255,.05);
}

.p-hdr{
    display:flex;
    justify-content:space-between;
    align-items:center;

    margin-bottom:10px;
}

.p-ttl{
    font-family:'Orbitron',monospace;
    font-size:.72rem;
    font-weight:700;

    color:#8ab4f8;

    letter-spacing:3px;
}

/* =========================================================
   BADGES
========================================================= */

.badge-live{
    padding:4px 12px;

    border-radius:20px;

    background:rgba(255,59,92,.10);

    border:1px solid #ff3b5c;

    color:#ff3b5c;

    font-size:.58rem;

    font-family:'Orbitron',monospace;
    letter-spacing:1px;
}

.badge-std{
    padding:4px 12px;

    border-radius:20px;

    background:rgba(255,255,255,.04);

    border:1px solid #334155;

    color:#94a3b8;

    font-size:.58rem;

    font-family:'Orbitron',monospace;
    letter-spacing:1px;
}

/* =========================================================
   FEED OFF
========================================================= */

.feed-off {
    background: radial-gradient(circle at center, #0b1120 0%, #05080d 70%);
    border: 1px dashed #1e3a5f;
    border-radius: 14px;
    width: 100%;
    aspect-ratio: 16 / 9;
    min-height: unset;
    max-height: unset;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 10px;
};

    border:1px dashed #1d3554;

    border-radius:16px;

    min-height:420px;

    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;

    gap:10px;
}

.fo-ico{
    font-size:3rem;
    opacity:.15;
}

.fo-ttl{
    font-family:'Orbitron',monospace;
    font-size:.75rem;

    color:#2f5d8d;

    letter-spacing:3px;
}

.fo-hint{
    font-size:.62rem;
    color:#2b4257;
}

/* =========================================================
   BOTONES
========================================================= */

div[data-testid="stButton"] > button{

    background:
    linear-gradient(
        90deg,
        #ff1744,
        #ff4d6d
    ) !important;

    border:none !important;

    color:white !important;

    border-radius:10px !important;

    height:46px !important;

    font-family:'Orbitron',monospace !important;
    font-size:.78rem !important;
    font-weight:700 !important;
    letter-spacing:2px !important;

    transition:.2s ease;
}

div[data-testid="stButton"] > button:hover{

    transform:translateY(-1px);

    box-shadow:
    0 0 18px rgba(255,59,92,.25);
}

/* =========================================================
   DOWNLOAD BUTTON
========================================================= */

.stDownloadButton > button{

    background:
    linear-gradient(
        90deg,
        #0ea5e9,
        #2563eb
    ) !important;

    border:none !important;

    color:white !important;

    border-radius:10px !important;

    height:44px !important;

    font-weight:700 !important;

    transition:.2s ease;
}

.stDownloadButton > button:hover{

    box-shadow:
    0 0 18px rgba(14,165,233,.25);
}

/* =========================================================
   SLIDER
========================================================= */

.stSlider label{
    color:#ffffff !important;
    font-size:.72rem !important;
    font-weight:700 !important;
}

/* =========================================================
   STATUS BAR
========================================================= */

.sbar{

    display:flex;
    align-items:center;
    flex-wrap:wrap;

    gap:16px;

    padding:9px 14px;

    margin-top:8px;

    background:#060a10;

    border:1px solid #1d3554;
    border-radius:8px;
}

.si{

    display:flex;
    align-items:center;
    gap:6px;

    font-family:'Orbitron',monospace;

    font-size:.58rem;

    color:#4f78a3;

    letter-spacing:1px;
}

.si-val{
    color:#00e5ff;
}

.dot-g{
    width:7px;
    height:7px;

    border-radius:50%;

    background:#00ff9d;

    box-shadow:
    0 0 10px #00ff9d;
}

.dot-r{
    width:7px;
    height:7px;

    border-radius:50%;

    background:#ff3b5c;

    box-shadow:
    0 0 10px #ff3b5c;
}

/* =========================================================
   DATAFRAME
========================================================= */

div[data-testid="stDataFrame"]{

    border-radius:14px;

    overflow:hidden;

    border:1px solid #1e293b;

    box-shadow:
    0 0 14px rgba(0,229,255,.04);
}

/* =========================================================
   PLOTLY
========================================================= */

.js-plotly-plot{

    border:1px solid #1e293b;

    border-radius:14px;

    padding:8px;

    background:#0b1120;

    box-shadow:
    0 0 12px rgba(0,229,255,.04);
}

/* =========================================================
   BOTTOM BAR
========================================================= */

.bbar{

    display:flex;
    justify-content:space-between;
    align-items:center;

    padding:10px 18px;

    min-height:45px;

    background:
    linear-gradient(
        145deg,
        #0b1120,
        #0d1726
    );

    border:1px solid #1e293b;
    border-radius:12px;

    margin-top:10px;
}

.bbar-txt{

    color:#4f78a3;

    font-size:.62rem;

    letter-spacing:1px;
}

/* =========================================================
   SCROLLBAR
========================================================= */

::-webkit-scrollbar{
    width:8px;
}

::-webkit-scrollbar-track{
    background:#030712;
}

::-webkit-scrollbar-thumb{
    background:#1e293b;
    border-radius:10px;
}

::-webkit-scrollbar-thumb:hover{
    background:#334155;
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

    # Captura estable; el ajuste visual se hace después a 16:9
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    return cap


def cerrar_camara():
    st.session_state.cam_on = False

    if st.session_state.cap is not None:
        st.session_state.cap.release()
        st.session_state.cap = None


def ajustar_frame_16_9(frame):
    alto, ancho = frame.shape[:2]

    nuevo_alto = int(ancho * 9 / 16)

    if nuevo_alto <= alto:
        y1 = (alto - nuevo_alto) // 2
        frame = frame[y1:y1 + nuevo_alto, :]
    else:
        nuevo_ancho = int(alto * 16 / 9)
        x1 = (ancho - nuevo_ancho) // 2
        frame = frame[:, x1:x1 + nuevo_ancho]

    frame = cv2.resize(frame, (960, 540))

    return frame


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

col_cam, col_tbl = st.columns([2.1, 1], gap="large")

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
        <div class="p-ttl">📋 ÚLTIMAS INCIDENCIAS ÁREA DE TORNO  </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not df.empty:
        columnas = [c for c in ["nombre", "tipo_incidencia", "hora"] if c in df.columns]

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

        # Ajusta el frame al mismo formato visual del dashboard
        frame = ajustar_frame_16_9(frame)

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
            use_container_width=True,
            output_format="JPEG"
        )

        sbar_slot.markdown(f"""
        <div class="sbar">
          <div class="si"><div class="dot-g"></div>MODELO: ACTIVO</div>
          <div class="si">FPS <span class="si-val">{st.session_state.fps:.1f}</span></div>
          <div class="si">DETECCIONES <span class="si-val">{detecciones}</span></div>
          <div class="si">CONF <span class="si-val">{st.session_state.conf_val:.2f}</span></div>
          <div class="si">RES <span class="si-val">960x540</span></div>
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

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

bc1, bc2 = st.columns([1, 4])

with bc1:
    if not df.empty:
        st.download_button(
            "📥 Exportar reporte",
            data=convertir_excel(datos),
            file_name=f"EPP_REPORTE_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

with bc2:
    st.markdown(f"""
    <div class="bbar">
      <span class="bbar-txt">
        EPP SCANNER · MONITOREO INTELIGENTE DE EQUIPO DE PROTECCIÓN PERSONAL · ÁREA DE TORNO
      </span>

      <span class="bbar-txt">
        {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
      </span>
    </div>
    """, unsafe_allow_html=True)