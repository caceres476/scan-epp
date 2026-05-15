import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Scanne EPP",
    page_icon="🧑‍🔧",
    layout="wide"
)

# 2. CARGA DE DATOS (Alacena)
def cargar_datos():
    if os.path.exists('datos.json'):
        with open('datos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

datos = cargar_datos()
df = pd.DataFrame(datos)

# 3. TÍTULO Y ENCABEZADO
st.title("SCANN EPP")
st.markdown(f"**TALLER DE TORNO**  Activo")
st.markdown("---")

# 4. FILA DE INDICADORES (Métricas)
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    total_alertas = len(df)
    alertas_hoy = len(df[df['fecha'] == '2026-04-29']) # Simulación de fecha actual
    confianza_avg = int(df['confianza_rekognition'].mean())
    
    col1.metric("Total de Incidencias", total_alertas)
    col2.metric("Alertas Hoy", alertas_hoy, delta="Pendientes")
    col3.metric("Confianza de IA", f"{confianza_avg}%")
    col4.metric("Área con más faltas", df['area'].mode()[0])

st.markdown("---")

# 5. CUERPO PRINCIPAL (Video y Tabla lado a lado)
col_video, col_tabla = st.columns([1.5, 1]) # La columna de video es más ancha

with col_video:
    st.subheader("Monitoreo de Cámara en Vivo")
    
    # SIMULACIÓN DE VIDEO (Mientras David conecta el suyo)
    # Aquí puedes poner un video de YouTube de "Detección de objetos" para que se vea pro
    st.video("https://www.youtube.com/watch?v=fXfSgRofVTo") 
    
    st.caption("Feed procesado mediante YOLO v8 - Análisis de Casco y Chaleco")

with col_tabla:
    st.subheader("Últimos Registros")
    if not df.empty:
        # Mostramos las columnas más importantes y los últimos 10 registros
        st.dataframe(
            df[['nombre', 'tipo_incidencia', 'hora', 'area']].tail(10),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay incidencias registradas aún.")

# 6. SECCIÓN DE ANÁLISIS (Gráficas)
st.markdown("---")
st.subheader("Análisis de Riesgos por Área")
col_grafica1, col_grafica2 = st.columns(2)

if not df.empty:
    with col_grafica1:
        st.write("**Incidencias por Empleado**")
        st.bar_chart(df['nombre'].value_counts())
    
    with col_grafica2:
        st.write("**Reportes por Área de Trabajo**")
        st.line_chart(df['area'].value_counts())

# 7. EL AUDITOR 
with st.expander("🔍 Auditoría de Datos Crudos (JSON)"):
    st.json(datos)
    
st.markdown("---")
st.subheader("Exportar Datos a Excel")

# Función para convertir el DataFrame a un Excel que se guarda en memoria
@st.cache_data
def convertir_a_excel(df_datos):
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_datos.to_excel(writer, index=False, sheet_name='Reporte_Incidencias')
    return output.getvalue()

if not df.empty:
    excel_data = convertir_a_excel(df)
    st.download_button(
        label="📄 Descargar Reporte en Excel",
        data=excel_data,
        file_name=f"Reporte_EPP_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.info("Este archivo contiene el historial completo para auditorías de seguridad.")
else:
    st.warning("No hay datos para exportar todavía.")