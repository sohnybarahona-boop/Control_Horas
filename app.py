import streamlit as st
import pandas as pd
import json
import os
from datetime import date

st.set_page_config(page_title="Control de Horas - Casas", page_icon="🏠", layout="wide")

DATA_FILE = "horas_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "horas_debo_1": 0.0,
        "horas_debo_2": 0.0,
        "casa1": [],
        "casa2": [],
        "counter_id": 10
    }

def save_data():
    data = {
        "horas_debo_1": st.session_state.get("horas_debo_1_input", 0.0),
        "horas_debo_2": st.session_state.get("horas_debo_2_input", 0.0),
        "casa1": st.session_state.casa1_df.to_dict(orient="records"),
        "casa2": st.session_state.casa2_df.to_dict(orient="records"),
        "counter_id": st.session_state.counter_id
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Cargar datos iniciales
saved = load_data()
if "casa1_df" not in st.session_state:
    st.session_state.casa1_df = pd.DataFrame(saved.get("casa1", []))
if "casa2_df" not in st.session_state:
    st.session_state.casa2_df = pd.DataFrame(saved.get("casa2", []))
if "counter_id" not in st.session_state:
    st.session_state.counter_id = saved.get("counter_id", 10)

st.title("🏠 Control y Registro de Horas")

def format_hours_minutes(decimal_hours):
    if pd.isna(decimal_hours) or decimal_hours < 0:
        return "0 hrs 0 min"
    hrs = int(decimal_hours)
    mins = int(round((decimal_hours - hrs) * 60))
    if mins == 60:
        hrs += 1
        mins = 0
    return f"{hrs} hrs y {mins} min"

# --- 1. RESUMEN GRÁFICO (ARRIBA DEL TODO) ---
st.header("📊 Resumen General")

col_d1, col_d2 = st.columns(2)
with col_d1:
    val_debo_1 = st.number_input("Horas que Debo - Casa 1", min_value=0.0, step=0.5, value=float(saved.get("horas_debo_1", 0.0)), key="horas_debo_1_input")
with col_d2:
    val_debo_2 = st.number_input("Horas que Debo - Casa 2", min_value=0.0, step=0.5, value=float(saved.get("horas_debo_2", 0.0)), key="horas_debo_2_input")

# Autoguardar de inmediato cualquier ajuste de horas debidas
save_data()

total_dev_1 = st.session_state.casa1_df["Horas Devengadas"].sum() if not st.session_state.casa1_df.empty else 0.0
total_dev_2 = st.session_state.casa2_df["Horas Devengadas"].sum() if not st.session_state.casa2_df.empty else 0.0

restante_1 = val_debo_1 - total_dev_1
restante_2 = val_debo_2 - total_dev_2

summary_table = [
    {
        "Casa": "Casa 1",
        "Horas Totales que Debo": format_hours_minutes(val_debo_1),
        "Horas Devengadas": format_hours_minutes(total_dev_1),
        "Horas Restantes": format_hours_minutes(restante_1 if restante_1 > 0 else 0.0),
        "Estado": "Completado" if restante_1 <= 0 and val_debo_1 > 0 else "Pendiente"
    },
    {
        "Casa": "Casa 2",
        "Horas Totales que Debo": format_hours_minutes(val_debo_2),
        "Horas Devengadas": format_hours_minutes(total_dev_2),
        "Horas Restantes": format_hours_minutes(restante_2 if restante_2 > 0 else 0.0),
        "Estado": "Completado" if restante_2 <= 0 and val_debo_2 > 0 else "Pendiente"
    }
]

st.dataframe(pd.DataFrame(summary_table), use_container_width=True, hide_index=True)

st.divider()

# --- 2. TRES PESTAÑAS ABAJO ---
tab1, tab2, tab3 = st.tabs(["📝 Registrar Horas", "🏠 Historial Casa 1", "🏡 Historial Casa 2"])

# PESTAÑA 1: REGISTRAR HORAS
with tab1:
    st.subheader("Registrar Nuevas Horas Devengadas")
    
    with st.form("form_registro_general"):
        casa_seleccionada = st.selectbox("Seleccionar Casa", ["Casa 1", "Casa 2"])
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fecha_reg = st.date_input("Fecha del Registro", value=date.today())
        with col_f2:
            num_horas = st.number_input("Horas", min_value=0, value=1, step=1)
            num_minutos = st.number_input("Minutos", min_value=0, max_value=59, value=0, step=5)
            
        btn_guardar_reg = st.form_submit_button("Guardar Registro")
        
        if btn_guardar_reg:
            total_decimal = num_horas + (num_minutos / 60.0)
            if total_decimal <= 0:
                st.error("Debes ingresar un valor mayor a 0 horas o minutos.")
            else:
                st.session_state.counter_id += 1
                new_entry = {
                    "ID": st.session_state.counter_id,
                    "Fecha": str(fecha_reg),
                    "Horas Devengadas": total_decimal
                }
                
                if casa_seleccionada == "Casa 1":
                    st.session_state.casa1_df = pd.concat([st.session_state.casa1_df, pd.DataFrame([new_entry])], ignore_index=True)
                else:
                    st.session_state.casa2_df = pd.concat([st.session_state.casa2_df, pd.DataFrame([new_entry])], ignore_index=True)
                
                save_data()
                st.success(f"¡Registro guardado y autoguardado exitosamente en {casa_seleccionada}!")
                st.rerun()

# PESTAÑA 2: HISTORIAL CASA 1
with tab2:
    st.subheader("Historial y Gestión - Casa 1")
    df1 = st.session_state.casa1_df
    
    if df1.empty:
        st.info("No hay registros guardados en la Casa 1.")
    else:
        display_df1 = df1.copy()
        display_df1["Tiempo Devengado"] = display_df1["Horas Devengadas"].apply(format_hours_minutes)
        st.dataframe(display_df1[["ID", "Fecha", "Tiempo Devengado"]], use_container_width=True, hide_index=True)
        
        st.markdown("#### Eliminar Registro")
        reg_opts_1 = {f"ID {row['ID']} - Fecha: {row['Fecha']} - Tiempo: {format_hours_minutes(row['Horas Devengadas'])}": row['ID'] for _, row in df1.iterrows()}
        
        selected_label_1 = st.selectbox("Selecciona el registro a eliminar", list(reg_opts_1.keys()), key="sel_casa1")
        sel_id_1 = reg_opts_1[selected_label_1]
        idx_1 = df1.index[df1['ID'] == sel_id_1].tolist()[0]
        
        if st.button("🗑️ Eliminar este registro de Casa 1", key="btn_del_1"):
            st.session_state.casa1_df = df1.drop(idx_1).reset_index(drop=True)
            save_data()
            st.success("¡Registro eliminado y guardado!")
            st.rerun()

# PESTAÑA 3: HISTORIAL CASA 2
with tab3:
    st.subheader("Historial y Gestión - Casa 2")
    df2 = st.session_state.casa2_df
    
    if df2.empty:
        st.info("No hay registros guardados en la Casa 2.")
    else:
        display_df2 = df2.copy()
        display_df2["Tiempo Devengado"] = display_df2["Horas Devengadas"].apply(format_hours_minutes)
        st.dataframe(display_df2[["ID", "Fecha", "Tiempo Devengado"]], use_container_width=True, hide_index=True)
        
        st.markdown("#### Eliminar Registro")
        reg_opts_2 = {f"ID {row['ID']} - Fecha: {row['Fecha']} - Tiempo: {format_hours_minutes(row['Horas Devengadas'])}": row['ID'] for _, row in df2.iterrows()}
        
        selected_label_2 = st.selectbox("Selecciona el registro a eliminar", list(reg_opts_2.keys()), key="sel_casa2")
        sel_id_2 = reg_opts_2[selected_label_2]
        idx_2 = df2.index[df2['ID'] == sel_id_2].tolist()[0]
        
        if st.button("🗑️ Eliminar este registro de Casa 2", key="btn_del_2"):
            st.session_state.casa2_df = df2.drop(idx_2).reset_index(drop=True)
            save_data()
            st.success("¡Registro eliminado y guardado!")
            st.rerun()
