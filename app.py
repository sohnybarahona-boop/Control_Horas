import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Control de Horas - Casas", page_icon="🏠", layout="wide")

st.title("🏠 Sistema de Control y Registro de Horas")
st.markdown("Gestiona las horas que debes, registra tus actividades devengadas y consulta el resumen general por propiedad.")

# Inicializar estado para las dos casas si no existe
if "casa1_df" not in st.session_state:
    st.session_state.casa1_df = pd.DataFrame([
        {"Fecha": "2026-09-01", "Descripción / Actividad": "Limpieza general y orden de habitaciones", "Categoría": "Mantenimiento", "Horas Devengadas": 5.0, "Observaciones": "Completado"},
        {"Fecha": "2026-09-10", "Descripción / Actividad": "Revisión de instalaciones eléctricas", "Categoría": "Reparación", "Horas Devengadas": 3.5, "Observaciones": "Sin novedad"},
    ])

if "casa2_df" not in st.session_state:
    st.session_state.casa2_df = pd.DataFrame([
        {"Fecha": "2026-09-05", "Descripción / Actividad": "Jardinería y áreas verdes", "Categoría": "Exteriores", "Horas Devengadas": 4.0, "Observaciones": "Completado"},
    ])

if "horas_debo" not in st.session_state:
    st.session_state.horas_debo = {"Casa 1": 40.0, "Casa 2": 40.0}

# --- SECCIÓN 1: RESUMEN GENERAL (ARRIBA) ---
st.header("📊 Resumen General")

total_casa1 = st.session_state.casa1_df["Horas Devengadas"].sum() if not st.session_state.casa1_df.empty else 0.0
total_casa2 = st.session_state.casa2_df["Horas Devengadas"].sum() if not st.session_state.casa2_df.empty else 0.0

debo_1 = st.session_state.horas_debo["Casa 1"]
debo_2 = st.session_state.horas_debo["Casa 2"]

restante_1 = debo_1 - total_casa1
restante_2 = debo_2 - total_casa2

summary_data = [
    {
        "Casa / Propiedad": "Casa 1",
        "Horas Totales que Debo": debo_1,
        "Horas Totales Devengadas": total_casa1,
        "Horas Restantes": restante_1,
        "Estado": "Completado" if restante_1 <= 0 else "Pendiente"
    },
    {
        "Casa / Propiedad": "Casa 2",
        "Horas Totales que Debo": debo_2,
        "Horas Totales Devengadas": total_casa2,
        "Horas Restantes": restante_2,
        "Estado": "Completado" if restante_2 <= 0 else "Pendiente"
    }
]

df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.session_state.horas_debo["Casa 1"] = st.number_input("Ajustar Horas que Debes - Casa 1", value=float(debo_1), step=1.0)
with col_s2:
    st.session_state.horas_debo["Casa 2"] = st.number_input("Ajustar Horas que Debes - Casa 2", value=float(debo_2), step=1.0)

st.divider()

# --- SECCIÓN 2: PESTAÑAS PARA CADA CASA Y REGISTRO / HISTORIAL ---
st.header("📝 Registro e Historial por Casa")
tab1, tab2 = st.tabs(["Casa 1", "Casa 2"])

def house_manager(house_name, df_key, debo_val):
    st.subheader(f"Historial y Registro de Horas - {house_name}")
    
    # Formulario para registrar horas
    with st.form(key=f"form_{house_name}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            f_fecha = st.date_input("Fecha")
        with col2:
            f_cat = st.selectbox("Categoría", ["Mantenimiento", "Reparación", "Exteriores", "Limpieza", "Otro"])
        with col3:
            f_horas = st.number_input("Horas Devengadas", min_value=0.0, step=0.5, value=1.0)
            
        f_desc = st.text_input("Descripción / Actividad")
        f_obs = st.text_input("Observaciones")
        
        submitted = st.form_submit_button("Registrar Horas")
        if submitted and f_desc:
            new_row = {
                "Fecha": str(f_fecha),
                "Descripción / Actividad": f_desc,
                "Categoría": f_cat,
                "Horas Devengadas": f_horas,
                "Observaciones": f_obs
            }
            st.session_state[df_key] = pd.concat([st.session_state[df_key], pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"¡Horas registradas exitosamente para {house_name}!")
            st.rerun()

    st.markdown("### Historial de Actividades")
    st.dataframe(st.session_state[df_key], use_container_width=True, hide_index=True)
    
    total_dev = st.session_state[df_key]["Horas Devengadas"].sum() if not st.session_state[df_key].empty else 0.0
    st.metric(label=f"Total Horas Devengadas ({house_name})", value=f"{total_dev:.2f} hrs")

with tab1:
    house_manager("Casa 1", "casa1_df", debo_1)

with tab2:
    house_manager("Casa 2", "casa2_df", debo_2)

st.divider()

# --- EXPORTAR A EXCEL ---
st.subheader("📥 Descargar Reporte en Excel")
if st.button("Generar Archivo Excel para Descarga"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Resumen General", index=False)
        st.session_state.casa1_df.to_excel(writer, sheet_name="Casa 1", index=False)
        st.session_state.casa2_df.to_excel(writer, sheet_name="Casa 2", index=False)
    
    processed_data = output.getvalue()
    st.download_button(
        label="📥 Descargar Excel con Resumen y Casas",
        data=processed_data,
        file_name="Control_Horas_Casas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
