import streamlit as st
import pandas as pd
import json
import os
import cv2
import time
import io
import pathlib
from datetime import datetime
import plotly.graph_objects as go

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
SAVE_DIR = ROOT_DIR / "Modulo_Rekognition_EPP" / "imagenes_incidentes"
DATA_PATH = BASE_DIR / "datos.json"

SAVE_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

.stApp {
    background: #071018;
    color: #e5edf5;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', 'Inter', sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding: 1rem 1.2rem 1.2rem 1.2rem !important;
    max-width: 100% !important;
}

/* NAVBAR */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 24px;
    background: #0d1b2a;
    border: 1px solid #1f3347;
    border-radius: 14px;
    margin-bottom: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,.22);
}

.nav-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: 1px;
    color: #f8fafc;
}

.nav-sub {
    font-size: .68rem;
    color: #8aa4bb;
    letter-spacing: 1.3px;
    margin-top: 4px;
    text-transform: uppercase;
}

.pill {
    padding: 6px 15px;
    border-radius: 999px;
    font-size: .66rem;
    font-weight: 700;
    letter-spacing: .8px;
}

.pill-on {
    background: rgba(47, 168, 125, .14);
    border: 1px solid #2fa87d;
    color: #6ee7b7;
}

.pill-off {
    background: rgba(220, 76, 100, .13);
    border: 1px solid #dc4c64;
    color: #fb7185;
}

/* MÉTRICAS */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 14px;
}

.mc {
    position: relative;
    background: #0d1b2a;
    border: 1px solid #1f3347;
    border-radius: 14px;
    padding: 15px;
    min-height: 96px;
    overflow: hidden;
    transition: .2s ease;
    box-shadow: 0 8px 20px rgba(0,0,0,.18);
}

.mc:hover {
    transform: translateY(-2px);
    border-color: #3b82a6;
    background: #102236;
}

.mc::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
}

.mc-b::before { background: #38bdf8; }
.mc-r::before { background: #fb7185; }
.mc-g::before { background: #34d399; }
.mc-y::before { background: #f59e0b; }

.mc-lbl {
    font-size: .62rem;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #8aa4bb;
    margin-bottom: 9px;
    font-weight: 700;
}

.mc-val {
    font-family: 'Inter', sans-serif;
    font-size: 1.65rem;
    font-weight: 800;
    color: #f8fafc;
}

.mc-sub {
    margin-top: 5px;
    font-size: .66rem;
    color: #6f879c;
}

/* PANELES */
.panel {
    background: #0d1b2a;
    border: 1px solid #1f3347;
    border-radius: 14px;
    padding: 13px 15px;
    box-shadow: 0 8px 20px rgba(0,0,0,.18);
}

.p-hdr {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.p-ttl {
    font-family: 'Inter', sans-serif;
    font-size: .75rem;
    font-weight: 800;
    color: #cbd5e1;
    letter-spacing: 1.4px;
    text-transform: uppercase;
}

/* BADGES */
.badge-live {
    padding: 4px 12px;
    border-radius: 999px;
    background: rgba(220, 76, 100, .14);
    border: 1px solid #dc4c64;
    color: #fb7185;
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .8px;
}

.badge-std {
    padding: 4px 12px;
    border-radius: 999px;
    background: rgba(148, 163, 184, .08);
    border: 1px solid #334155;
    color: #94a3b8;
    font-size: .62rem;
    font-weight: 700;
    letter-spacing: .8px;
}

/* FEED APAGADO */
.feed-off {
    background: #080f17;
    border: 1px dashed #28445c;
    border-radius: 14px;
    width: 100%;
    aspect-ratio: 16 / 9;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 10px;
}

.fo-ico {
    font-size: 3rem;
    opacity: .18;
}

.fo-ttl {
    font-size: .78rem;
    color: #6f879c;
    letter-spacing: 1.8px;
    font-weight: 800;
}

.fo-hint {
    font-size: .68rem;
    color: #536b7f;
}

/* BOTONES */
div[data-testid="stButton"] > button {
    background: #dc4c64 !important;
    border: 1px solid #ef6b80 !important;
    color: white !important;
    border-radius: 10px !important;
    height: 44px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .76rem !important;
    font-weight: 800 !important;
    letter-spacing: .8px !important;
    transition: .2s ease;
}

div[data-testid="stButton"] > button:hover {
    background: #ef5f78 !important;
    box-shadow: 0 8px 18px rgba(220,76,100,.20);
}

/* SLIDER */
.stSlider label {
    color: #e5edf5 !important;
    font-size: .72rem !important;
    font-weight: 700 !important;
}

div[data-baseweb="slider"] > div {
    color: #38bdf8 !important;
}

/* STATUS BAR */
.sbar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    padding: 9px 14px;
    margin-top: 8px;
    background: #08121c;
    border: 1px solid #1f3347;
    border-radius: 8px;
}

.si {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: .62rem;
    color: #8aa4bb;
    letter-spacing: .8px;
    font-weight: 700;
}

.si-val {
    color: #7dd3fc;
}

.dot-g {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #34d399;
}

.dot-r {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #fb7185;
}

/* TABLA */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #1f3347;
    box-shadow: 0 8px 20px rgba(0,0,0,.16);
}

/* GRÁFICAS */
.chart-title {
    font-family: 'Inter', sans-serif;
    font-size: .74rem;
    color: #fbbf24;
    letter-spacing: 1.2px;
    margin-bottom: 10px;
    font-weight: 800;
    text-transform: uppercase;
}

.js-plotly-plot {
    background: transparent !important;
}

/* CONTENEDORES STREAMLIT */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #0d1b2a !important;
    border: 1px solid #1f3347 !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 20px rgba(0,0,0,.16);
}

/* BOTÓN DESCARGA */
.stDownloadButton > button {
    background: #1d7fa8 !important;
    border: 1px solid #38bdf8 !important;
    color: white !important;
    border-radius: 10px !important;
    height: 42px !important;
    font-weight: 800 !important;
}

.stDownloadButton > button:hover {
    background: #2493c2 !important;
    box-shadow: 0 8px 18px rgba(56,189,248,.18);
}

/* BARRA FINAL */
.bbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 18px;
    min-height: 44px;
    background: #0d1b2a;
    border: 1px solid #1f3347;
    border-radius: 12px;
    margin-top: 10px;
}

.bbar-txt {
    color: #8aa4bb;
    font-size: .64rem;
    letter-spacing: .8px;
}

/* SCROLL */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #071018;
}

::-webkit-scrollbar-thumb {
    background: #28445c;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #3b5f7a;
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


def grafica_horizontal(serie):
    colores = [
        "#00E5FF",
        "#FF3B5C",
        "#FBBF24",
        "#00FF9D",
        "#8B5CF6",
        "#38BDF8",
        "#F97316",
    ]

    serie = serie.sort_values(ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=serie.values,
        y=serie.index,
        orientation="h",
        marker=dict(
            color=colores[:len(serie)],
            line=dict(color="rgba(255,255,255,0.18)", width=1)
        ),
        text=serie.values,
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(color="#ffffff", size=12),
        hovertemplate="<b>%{y}</b><br>Total: %{x}<extra></extra>"
    ))

    fig.update_layout(
    height=250,
    margin=dict(l=10, r=10, t=5, b=5),

    paper_bgcolor="#0d1b2a",
    plot_bgcolor="#0d1b2a",

    font=dict(
        color="#E5EDF5",
        size=11,
        family="IBM Plex Sans"
    ),

    xaxis=dict(
        showgrid=False,
        zeroline=False,
        visible=False
    ),

    yaxis=dict(
        showgrid=False,
        zeroline=False,
        tickfont=dict(
            color="#C9D8E8",
            size=11
        )
    ),

    bargap=0.35,
)

    return fig


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
    <div class="nav-sub">SISTEMA DE DETECCIÓN · ÁREA DE TORNO · YOLO</div>
  </div>
  <div style="display:flex; align-items:center; gap:18px;">
    {pill}
    <div style="font-family:Orbitron; font-size:.7rem; color:#4f78a3; letter-spacing:2px;">
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
conf_prom = f"{int(st.session_state.conf_val * 100)}%"
area_critica = df["area"].mode()[0] if not df.empty and "area" in df.columns else "Torno"

st.markdown(f"""
<div class="metric-grid">
  <div class="mc mc-b">
    <div class="mc-lbl">Total incidencias</div>
    <div class="mc-val">{total}</div>
    <div class="mc-sub">Historial completo</div>
  </div>
  <div class="mc mc-r">
    <div class="mc-lbl">Alertas hoy</div>
    <div class="mc-val">{alertas_hoy}</div>
    <div class="mc-sub">Eventos del día</div>
  </div>
  <div class="mc mc-g">
    <div class="mc-lbl">Confianza IA</div>
    <div class="mc-val">{conf_prom}</div>
    <div class="mc-sub">Nivel mínimo de detección</div>
  </div>
  <div class="mc mc-y">
    <div class="mc-lbl">Área monitoreada</div>
    <div class="mc-val" style="font-size:1.05rem;padding-top:6px"> ÁREA DE TORNO </div>
    <div class="mc-sub">Zona operativa</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# CUERPO PRINCIPAL
# ═══════════════════════════════════════════════════════════

col_cam, col_tbl = st.columns([2.15, 1], gap="large")

with col_cam:
    live_badge = '<span class="badge-live">● REC</span>' if st.session_state.cam_on else '<span class="badge-std">STANDBY</span>'

    st.markdown(f"""
    <div class="panel">
      <div class="p-hdr">
        <div class="p-ttl">📡 MONITOREO EN VIVO</div>
        {live_badge}
      </div>
    </div>
    """, unsafe_allow_html=True)

    b1, b2 = st.columns([1, 3])

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
        st.slider(
            "Confianza mínima",
            0.30,
            0.95,
            0.70,
            0.05,
            format="%.2f",
            key="conf_val"
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
    <div class="panel">
      <div class="p-hdr">
        <div class="p-ttl">📋 ÚLTIMAS INCIDENCIAS ÁREA DE TORNO</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not df.empty:
        columnas = [c for c in ["nombre", "tipo_incidencia", "hora"] if c in df.columns]

        st.dataframe(
            df[columnas].tail(12).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            height=540,
        )
    else:
        st.info("Sin registros aún.")
# ═══════════════════════════════════════════════════════════
# GRÁFICAS HORIZONTALES
# ═══════════════════════════════════════════════════════════

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

if not df.empty:

    gc1, gc2 = st.columns(2, gap="large")

    # ─────────────────────────────────────────────
    # GRÁFICA EMPLEADOS
    # ─────────────────────────────────────────────
    with gc1:

        with st.container(border=True):

            st.markdown(
                '<div class="chart-title">◇ INCIDENCIAS POR EMPLEADO</div>',
                unsafe_allow_html=True
            )

            if "nombre" in df.columns:

                serie_empleados = (
                    df["nombre"]
                    .value_counts()
                    .head(6)
                )

                fig_empleados = grafica_horizontal(
                    serie_empleados
                )

                st.plotly_chart(
                    fig_empleados,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    }
                )

    # ─────────────────────────────────────────────
# GRÁFICA EPP CON MAYOR INCUMPLIMIENTO
# ─────────────────────────────────────────────
with gc2:

    with st.container(border=True):

        st.markdown(
            '<div class="chart-title">◇ EPP CON MAYOR INCUMPLIMIENTO</div>',
            unsafe_allow_html=True
        )

        equipos_epp = {
            "Casco": 24,
            "Mascarilla": 18,
            "Chaleco": 20,
            "Guantes": 14
        }

        serie_epp = pd.Series(equipos_epp)

        fig_epp = grafica_horizontal(
            serie_epp
        )

        st.plotly_chart(
            fig_epp,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

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