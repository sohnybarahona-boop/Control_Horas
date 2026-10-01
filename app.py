from datetime import date, datetime
import json
import os
import streamlit as st

# Archivo local donde se guardarán los datos de forma persistente
DATA_FILE = "data.json"


def cargar_datos():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return []
  return []


def guardar_datos(registros):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(registros, f, ensure_ascii=False, indent=4)


# Configuración de la página
st.set_page_config(
    page_title="Control de Horas", page_icon="⏱️", layout="centered"
)

# Cargar los registros existentes
registros = cargar_datos()

# Menú superior estilo pestañas
menu = st.radio(
    "Navegación",
    ["Registrar Horas", "Ver / Corregir Historial"],
    label_visibility="collapsed",
    horizontal=True,
)

st.markdown("---")

# ==========================================
# SECCIÓN 1: REGISTRAR HORAS
# ==========================================
if menu == "Registrar Horas":
  st.subheader("Registrar Nuevas Horas")

  with st.form("form_registro", clear_on_submit=True):
    casa = st.text_input("Nombre de la Casa (ej. Casa #1, Casa #2)")
    horas = st.number_input(
        "Cantidad de Horas", min_value=0.5, step=0.5, value=1.0
    )
    fecha = st.date_input("Fecha", value=date.today())
    nota = st.text_area("Nota o descripción (opcional)")

    submitted = st.form_submit_button("Guardar Registro")
    if submitted:
      if casa.strip():
        # Generar un ID único basado en el tiempo actual
        nuevo_id = f"{len(registros) + 1}_{datetime.now().timestamp()}"
        nuevo_registro = {
            "id": nuevo_id,
            "casa": casa.strip(),
            "horas": horas,
            "fecha": str(fecha),
            "nota": nota,
        }
        registros.append(nuevo_registro)
        guardar_datos(registros)
        st.success("¡Registro guardado con éxito!")
        st.rerun()
      else:
        st.error("Por favor, indica el nombre de la casa.")

# ==========================================
# SECCIÓN 2: HISTORIAL CON PESTAÑAS Y OPCIÓN DE EDITAR/BORRAR
# ==========================================
elif menu == "Ver / Corregir Historial":
  st.subheader("Historial de registros y correcciones")
  st.write(
      "Puedes **eliminar** un registro o **editarlo** directamente si te"
      " equivocaste en algo:"
  )

  if not registros:
    st.info("No hay registros guardados todavía.")
  else:
    # Obtener la lista única de casas
    casas_disponibles = sorted(list(set(reg["casa"] for reg in registros)))

    if casas_disponibles:
      # Crear una pestaña por cada casa
      pestanas = st.tabs(casas_disponibles)

      for i, casa in enumerate(casas_disponibles):
        with pestanas[i]:
          st.markdown(f"### Registros de {casa}")

          # Filtrar los registros de esta casa
          registros_casa = [reg for reg in registros if reg["casa"] == casa]

          for reg in registros_casa:
            st.markdown(
                f"**{reg['casa']} - {reg['horas']} hrs** ({reg['fecha']})"
            )
            if reg.get("nota"):
              st.write(f"Nota: {reg['nota']}")

            # Botones de Borrar y Editar lado a lado
            col1, col2 = st.columns(2)

            with col1:
              if st.button("🗑️ Borrar", key=f"borrar_{reg['id']}"):
                registros = [r for r in registros if r["id"] != reg["id"]]
                guardar_datos(registros)
                st.success("Registro eliminado correctamente.")
                st.rerun()

            with col2:
              if st.button("✏️ Editar", key=f"btn_edit_{reg['id']}"):
                st.session_state[f"editando_{reg['id']}"] = True

            # Si se presionó editar, se abre un pequeño formulario para cambiar los datos
            if st.session_state.get(f"editando_{reg['id']}", False):
              with st.form(key=f"form_edit_{reg['id']}"):
                st.markdown(f"**Modificar registro:**")
                nuevo_casa = st.text_input("Casa", value=reg["casa"])
                nuevas_horas = st.number_input(
                    "Horas",
                    min_value=0.5,
                    step=0.5,
                    value=float(reg["horas"]),
                )

                try:
                  fecha_obj = datetime.strptime(
                      reg["fecha"], "%Y-%m-%d"
                  ).date()
                except:
                  fecha_obj = date.today()

                nueva_fecha = st.date_input("Fecha", value=fecha_obj)
                nueva_nota = st.text_area("Nota", value=reg.get("nota", ""))

                c_guardar, c_cancelar = st.columns(2)
                if c_guardar.form_submit_button("Guardar Cambios"):
                  for r in registros:
                    if r["id"] == reg["id"]:
                      r["casa"] = nuevo_casa.strip()
                      r["horas"] = nuevas_horas
                      r["fecha"] = str(nueva_fecha)
                      r["nota"] = nueva_nota
                  guardar_datos(registros)
                  st.session_state[f"editando_{reg['id']}"] = False
                  st.success("¡Modificado con éxito!")
                  st.rerun()

                if c_cancelar.form_submit_button("Cancelar"):
                  st.session_state[f"editando_{reg['id']}"] = False
                  st.rerun()

            st.markdown("---")
