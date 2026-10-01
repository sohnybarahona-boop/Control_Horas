import streamlit as st
import pandas as pd
import io
import json

st.set_page_config(page_title="Control de Horas - Casas", page_icon="🏠", layout="wide")

st.title("🏠 Sistema de Control y Registro de Horas")
st.markdown("Gestiona las horas que debes, registra, edita o elimina actividades devengadas y consulta el resumen general.")

# 1. Inicializar estados
if "casa1_df" not in st.session_state:
    st.session_state.casa1_df = pd.DataFrame(columns=["ID", "Fecha", "Horas Devengadas", "Observaciones"])

if "casa2_df" not in st.session_state:
    st.session_state.casa2_df = pd.DataFrame(columns=["ID", "Fecha", "Horas Devengadas", "Observaciones"])

if "horas_debo_1" not in st.session_state:
    st.session_state.horas_debo_1 = 0.0

if "horas_debo_2" not in st.session_state:
    st.session_state.horas_debo_2 = 0.0

if "counter_id" not in st.session_state:
    st.session_state.counter_id = 10

# --- SECCIÓN DE RESPALDO (CARGAR / DESCARGAR DATOS) ---
with st.expander("💾 Respaldar o Recuperar tus Datos (Evita perder información)", expanded=False):
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        st.markdown("**Guardar Respaldo Actual**")
        backup_data = {
            "horas_debo_1": st.session_state.horas_debo_1,
            "horas_debo_2": st.session_state.horas_debo_2,
            "casa1": st.session_state.casa1_df.to_dict(orient="records"),
            "casa2": st.session_state.casa2_df.to_dict(orient="records"),
            "counter_id": st.session_state.counter_id
        }
        st.download_button(
            label="📥 Descargar Archivo de Respaldo (.json)",
            data=json.dumps(backup_data, ensure_ascii=False, indent=4),
            file_name="respaldo_horas.json",
            mime="application/json"
        )
        
    with col_b2:
        st.markdown("**Restaurar Datos Anteriores**")
        uploaded_file = st.file_uploader("Sube tu archivo de respaldo (.json)", type=["json"])
        if uploaded_file is not None:
            try:
                loaded_data = json.load(uploaded_file)
                st.session_state.horas_debo_1 = loaded_data.get("horas_debo_1", 0.0)
                st.session_state.horas_debo_2 = loaded_data.get("horas_debo_2", 0.0)
                st.session_state.casa1_df = pd.DataFrame(loaded_data.get("casa1", []))
                st.session_state.casa2_df = pd.DataFrame(loaded_data.get("casa2", []))
                st.session_state.counter_id = loaded_data.get("counter_id", 10)
                st.success("¡Datos restaurados con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

st.divider()

# --- SECCIÓN 1: RESUMEN GENERAL (ARRIBA) ---
st.header("📊 Resumen General")

col_s1, col_s2 = st.columns(2)
with col_s1:
    debo_1 = st.number_input("Ajustar Horas que Debes - Casa 1", min_value=0.0, step=1.0, key="horas_debo_1")
with col_s2:
    debo_2 = st.number_input("Ajustar Horas que Debes - Casa 2", min_value=0.0, step=1.0, key="horas_debo_2")

total_casa1 = st.session_state.casa1_df["Horas Devengadas"].sum() if not st.session_state.casa1_df.empty else 0.0
total_casa2 = st.session_state.casa2_df["Horas Devengadas"].sum() if not st.session_state.casa2_df.empty else 0.0

restante_1 = debo_1 - total_casa1
restante_2 = debo_2 - total_casa2

summary_data = [
    {
        "Casa / Propiedad": "Casa 1",
        "Horas Totales que Debo": debo_1,
        "Horas Totales Devengadas": total_casa1,
        "Horas Restantes": restante_1,
        "Estado": "Completado" if restante_1 <= 0 and debo_1 > 0 else "Pendiente"
    },
    {
        "Casa / Propiedad": "Casa 2",
        "Horas Totales que Debo": debo_2,
        "Horas Totales Devengadas": total_casa2,
        "Horas Restantes": restante_2,
        "Estado": "Completado" if restante_2 <= 0 and debo_2 > 0 else "Pendiente"
    }
]

df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

st.divider()

# --- SECCIÓN 2: PESTAÑAS PARA CADA CASA (REGISTRO, EDICIÓN Y ELIMINACIÓN) ---
st.header("📝 Registro, Edición e Historial por Casa")
tab1, tab2 = st.tabs(["Casa 1", "Casa 2"])

def house_manager(house_name, df_key):
    st.subheader(f"Gestión de Actividades - {house_name}")
    
    # 1. Formulario para Agregar Nuevo Registro
    with st.expander("➕ Agregar Nuevo Registro de Horas", expanded=False):
        with st.form(key=f"form_add_{house_name}"):
            col1, col2 = st.columns(2)
            with col1:
                f_fecha = st.date_input("Fecha", key=f"add_f_{house_name}")
            with col2:
                f_horas = st.number_input("Horas Devengadas", min_value=0.0, step=0.5, value=1.0, key=f"add_h_{house_name}")
                
            f_obs = st.text_input("Observaciones / Actividad", key=f"add_o_{house_name}")
            
            submitted = st.form_submit_button("Guardar Nuevo Registro")
            if submitted:
                st.session_state.counter_id += 1
                new_row = {
                    "ID": st.session_state.counter_id,
                    "Fecha": str(f_fecha),
                    "Horas Devengadas": f_horas,
                    "Observaciones": f_obs
                }
                st.session_state[df_key] = pd.concat([st.session_state[df_key], pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"¡Registro agregado exitosamente en {house_name}!")
                st.rerun()

    # Mostrar tabla actual
    df = st.session_state[df_key]
    st.markdown("### Historial de Actividades")
    if df.empty:
        st.info("No hay registros todavía.")
        return

    st.dataframe(df, use_container_width=True, hide_index=True)
    
    total_dev = df["Horas Devengadas"].sum()
    st.metric(label=f"Total Horas Devengadas ({house_name})", value=f"{total_dev:.2f} hrs")

    st.divider()
    
    # 2. Sección para Editar o Eliminar registros existentes
    st.markdown("### ✏️ Editar o 🗑️ Eliminar Registro Existente")
    
    record_options = {f"ID {row['ID']} - {row['Fecha']} - {row['Observaciones']}": row['ID'] for _, row in df.iterrows()}
    
    if record_options:
        selected_label = st.selectbox("Selecciona el registro a modificar o eliminar", list(record_options.keys()), key=f"sel_{house_name}")
        selected_id = record_options[selected_label]
        
        record_idx = df.index[df['ID'] == selected_id].tolist()[0]
        curr_row = df.loc[record_idx]
        
        col_ed1, col_ed2 = st.columns(2)
        
        with col_ed1:
            st.markdown("#### Editar Registro")
            with st.form(key=f"form_edit_{house_name}_{selected_id}"):
                edit_fecha = st.text_input("Fecha (YYYY-MM-DD)", value=str(curr_row["Fecha"]))
                edit_horas = st.number_input("Horas Devengadas", value=float(curr_row["Horas Devengadas"]), step=0.5)
                edit_obs = st.text_input("Observaciones / Actividad", value=str(curr_row["Observaciones"]))
                
                update_btn = st.form_submit_button("Actualizar Registro")
                if update_btn:
                    st.session_state[df_key].loc[record_idx, "Fecha"] = edit_fecha
                    st.session_state[df_key].loc[record_idx, "Horas Devengadas"] = edit_horas
                    st.session_state[df_key].loc[record_idx, "Observaciones"] = edit_obs
                    st.success("¡Registro actualizado con éxito!")
                    st.rerun()
                    
        with col_ed2:
            st.markdown("#### Eliminar Registro")
            st.warning("Esta acción borrará el registro seleccionado permanentemente.")
            if st.button("🗑️ Eliminar este registro", key=f"del_btn_{house_name}_{selected_id}"):
                st.session_state[df_key] = df.drop(record_idx).reset_index(drop=True)
                st.success("¡Registro eliminado correctamente!")
                st.rerun()

with tab1:
    house_manager("Casa 1", "casa1_df")

with tab2:
    house_manager("Casa 2", "casa2_df")

st.divider()

# --- EXPORTAR A EXCEL ---
st.subheader("📥 Descargar Reporte en Excel")
if st.button("Generar Archivo Excel para Descarga"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Resumen General", index=False)
        st.session_state.casa1_df.drop(columns=["ID"], errors="ignore").to_excel(writer, sheet_name="Casa 1", index=False)
        st.session_state.casa2_df.drop(columns=["ID"], errors="ignore").to_excel(writer, sheet_name="Casa 2", index=False)
    
    processed_data = output.getvalue()
    st.download_button(
        label="📥 Descargar Excel con Resumen y Casas",
        data=processed_data,
        file_name="Control_Horas_Casas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
