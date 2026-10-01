from datetime import datetime
import json
import os
import streamlit as st

# Archivo local para guardar los datos
DATA_FILE = "data.json"


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  else:
    return {"debt_casa_1": 48.5, "debt_casa_2": 23.5, "history": []}


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# Cargar datos
data = load_data()

st.title("⏱️ Control de Horas de Trabajo")

# Calcular horas restantes
total_worked_casa_1 = sum(
    item["hours"] for item in data["history"] if item["casa"] == "Casa #1"
)
total_worked_casa_2 = sum(
    item["hours"] for item in data["history"] if item["casa"] == "Casa #2"
)

current_debt_1 = max(0.0, data["debt_casa_1"] - total_worked_casa_1)
current_debt_2 = max(0.0, data["debt_casa_2"] - total_worked_casa_2)

# Mostrar estado actual de las deudas en métricas
col1, col2 = st.columns(2)
col1.metric(
    label="🏠 Deuda Casa #1",
    value=f"{current_debt_1:.1f} hrs",
    delta=f"-{total_worked_casa_1:.1f} hrs trabajadas",
)
col2.metric(
    label="🏡 Deuda Casa #2",
    value=f"{current_debt_2:.1f} hrs",
    delta=f"-{total_worked_casa_2:.1f} hrs trabajadas",
)

st.divider()

# Pestañas para organizar la app y permitir correcciones
tab1, tab2 = st.tabs(["➕ Registrar Horas", "✏️ Ver / Corregir Historial"])

with tab1:
  st.subheader("Registrar nueva jornada")
  with st.form("form_horas"):
    casa_seleccionada = st.selectbox(
        "¿Dónde realizaste el trabajo?", ["Casa #1", "Casa #2"]
    )
    horas_ingresadas = st.number_input(
        "Cantidad de horas:", min_value=0.5, max_value=24.0, step=0.5, value=1.0
    )
    fecha_trabajo = st.date_input("Fecha:", value=datetime.now())
    nota = st.text_input("Nota o descripción (opcional):", "")

    submitted = st.form_submit_button("Guardar Registro")
    if submitted:
      nuevo_registro = {
          "id": datetime.now().strftime("%Y%m%d%H%M%S"),
          "casa": casa_seleccionada,
          "hours": horas_ingresadas,
          "date": fecha_trabajo.strftime("%Y-%m-%d"),
          "note": nota,
      }
      data["history"].append(nuevo_registro)
      save_data(data)
      st.success("¡Registro guardado con éxito!")
      st.rerun()

with tab2:
  st.subheader("Historial de registros y correcciones")
  if not data["history"]:
    st.info(
        "Aún no hay registros guardados. ¡Usa la pestaña de registrar para"
        " empezar!"
    )
  else:
    st.write(
        "Si te equivocaste en algún registro, puedes **eliminarlo** aquí y"
        " volver a ingresarlo correctamente:"
    )

    for i, item in enumerate(reversed(data["history"])):
      with st.container():
        col_info, col_btn = st.columns([4, 1])
        with col_info:
          st.markdown(
              f"**{item['casa']}** - **{item['hours']} hrs** ({item['date']})"
          )
          if item["note"]:
            st.caption(f"Nota: {item['note']}")
        with col_btn:
          if st.button("🗑️ Borrar", key=f"del_{item['id']}_{i}"):
            data["history"] = [
                h for h in data["history"] if h["id"] != item["id"]
            ]
            save_data(data)
            st.success("Registro eliminado correctamente.")
            st.rerun()
        st.divider()
