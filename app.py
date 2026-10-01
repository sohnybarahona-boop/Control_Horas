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
        datos = json.load(f)
        # Asegurar que lo que se carga es una lista, si no, devolver lista vacía
        if isinstance(datos, list):
          return datos
        else:
          return []
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

# Cargar los registros existentes asegurando que sea una lista
registros = cargar_datos()
if not isinstance(registros, list):
  registros = []

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
        # Volver a cargar los datos por seguridad antes de agregar
        registros_actuales = cargar_datos()
        if not isinstance(registros_actuales, list):
          registros_actuales = []

        nuevo_id = f"{len(registros_actuales) + 1}_{datetime.now().timestamp()}"
        nuevo_registro = {
            "id": nuevo_id,
            "casa": casa.strip(),
            "horas": horas,
            "fecha": str(fecha),
            "nota": nota,
        }
        registros_actuales.append(nuevo_registro)
        guardar_datos(registros_actuales)
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
    # Obtener la lista única de casas de forma segura
    casas_disponibles = sorted(
        list(
            set(
                reg.get("casa", "Casa Desconocida")
                for reg in registros
                if isinstance(reg, dict)
            )
        )
    )

    if casas_disponibles:
      # Crear una pestaña por cada casa
      pestanas = st.tabs(casas_disponibles)

      for i, casa in enumerate(casas_disponibles):
        with pestanas[i]:
          st.markdown(f"### Registros de {casa}")

          # Filtrar los registros de esta casa de forma segura
          registros_casa = [
              reg
              for reg in registros
              if isinstance(reg, dict)
              and reg.get("casa", "Casa Desconocida") == casa
          ]

          for reg in registros_casa:
            reg_id = reg.get("id", str(datetime.now().timestamp()))
            reg_casa = reg.get("casa", "Sin casa")
            reg_horas = reg.get("horas", 0)
            reg_fecha = reg.get("fecha", "")
            reg_nota = reg.get("nota", "")

            st.markdown(f"**{reg_casa} - {reg_horas} hrs** ({reg_fecha})")
            if reg_nota:
              st.write(f"Nota: {reg_nota}")

            # Botones de Borrar y Editar lado a lado
            col1, col2 = st.columns(2)

            with col1:
              if st.button("🗑️ Borrar", key=f"borrar_{reg_id}"):
                datos_actuales = cargar_datos()
                if isinstance(datos_actuales, list):
                  datos_actuales = [
                      r for r in datos_actuales if r.get("id") != reg_id
                  ]
                  guardar_datos(datos_actuales)
                st.success("Registro eliminado correctamente.")
                st.rerun()

            with col2:
              if st.button("✏️ Editar", key=f"btn_edit_{reg_id}"):
                st.session_state[f"editando_{reg_id}"] = True

            # Si se presionó editar, se abre un pequeño formulario
            if st.session_state.get(f"editando_{reg_id}", False):
              with st.form(key=f"form_edit_{reg_id}"):
                st.markdown(f"**Modificar registro:**")
                nuevo_casa = st.text_input("Casa", value=reg_casa)
                nuevas_horas = st.number_input(
                    "Horas", min_value=0.5, step=0.5, value=float(reg_horas)
                )

                try:
                  fecha_obj = datetime.strptime(reg_fecha, "%Y-%m-%d").date()
                except:
                  fecha_obj = date.today()

                nueva_fecha = st.date_input("Fecha", value=fecha_obj)
                nueva_nota = st.text_area("Nota", value=reg_nota)

                c_guardar, c_cancelar = st.columns(2)
                if c_guardar.form_submit_button("Guardar Cambios"):
                  datos_actuales = cargar_datos()
                  if isinstance(datos_actuales, list):
                    for r in datos_actuales:
                      if r.get("id") == reg_id:
                        r["casa"] = nuevo_casa.strip()
                        r["horas"] = nuevas_horas
                        r["fecha"] = str(nueva_fecha)
                        r["nota"] = nueva_nota
                    guardar_datos(datos_actuales)
                  st.session_state[f"editando_{reg_id}"] = False
                  st.success("¡Modificado con éxito!")
                  st.rerun()

                if c_cancelar.form_submit_button("Cancelar"):
                  st.session_state[f"editando_{reg_id}"] = False
                  st.rerun()

            st.markdown("---")
