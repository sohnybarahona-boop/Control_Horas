import json
import os
from datetime import datetime
import streamlit as st

# Configuración de la página web
st.set_page_config(page_title="Control de Horas de Trabajo", page_icon="⏱️", layout="centered")

FILENAME = "registro_horas.json"

def cargar_datos():
    """Carga los datos del archivo JSON o inicializa las deudas por defecto."""
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    
    return {
        "Casa #1": {
            "deuda_inicial_minutos": (48 * 60) + 30, # 48h 30m
            "registros": []
        },
        "Casa #2": {
            "deuda_inicial_minutos": (23 * 60) + 30, # 23h 30m
            "registros": []
        }
    }

def guardar_datos(datos):
    """Guarda los datos actualizados en el archivo JSON."""
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def minutos_a_horas_minutos(total_minutos):
    """Convierte minutos totales a un formato legible de horas y minutos."""
    if total_minutos < 0:
        return f"-{-total_minutos // 60}h {-(-total_minutos % 60)}m (¡Superado!)"
    horas = total_minutos // 60
    minutos = total_minutos % 60
    return f"{horas}h {minutos}m"

# Cargar datos en la app
datos = cargar_datos()

st.title("⏱️ Control de Horas de Trabajo (Vacaciones)")
st.write("Registra tus horas devengadas y consulta el estado de tus deudas en tiempo real.")

# --- SECCIÓN 1: RESUMEN (TABLA) ---
st.subheader("📊 Resumen Actual")

resumen_data = []
for casa, info in datos.items():
    deuda_inicial = info["deuda_inicial_minutos"]
    total_devengado = sum(r["minutos"] for r in info["registros"])
    pendiente = deuda_inicial - total_devengado
    
    resumen_data.append({
        "Casa": casa,
        "Deuda Inicial": minutos_a_horas_minutos(deuda_inicial),
        "Total Devengado": minutos_a_horas_minutos(total_devengado),
        "Pendiente": minutos_a_horas_minutos(pendiente)
    })

st.table(resumen_data)

# --- SECCIÓN 2: FORMULARIO PARA REGISTRAR HORAS ---
st.subheader("➕ Registrar Nuevas Horas")

with st.form("form_registro"):
    casa_seleccionada = st.selectbox("Selecciona la casa:", ["Casa #1", "Casa #2"])
    
    col1, col2 = st.columns(2)
    with col1:
        horas = st.number_input("Horas trabajadas", min_value=0, step=1, value=0)
    with col2:
        minutos = st.number_input("Minutos trabajados", min_value=0, max_value=59, step=1, value=0)
        
    nota = st.text_input("Nota o comentario (opcional):", placeholder="Ej. Turno matutino")
    
    submit_button = st.form_submit_button(label="Guardar Registro")

if submit_button:
    total_nuevos_minutos = (horas * 60) + minutos
    if total_nuevos_minutos <= 0:
        st.error("Por favor, ingresa una cantidad de tiempo mayor a cero.")
    else:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Guardar en la estructura
        datos[casa_seleccionada]["registros"].append({
            "fecha": fecha,
            "minutos": total_nuevos_minutos,
            "nota": nota
        })
        
        guardar_datos(datos)
        st.success(f"¡Se han registrado {horas}h {minutos}m en {casa_seleccionada} con éxito!")
        st.rerun()

# --- SECCIÓN 3: HISTORIAL DETALLADO ---
st.subheader("📜 Historial de Registros")
for casa, info in datos.items():
    with st.expander(f"Ver historial de {casa}"):
        if not info["registros"]:
            st.info("No hay registros todavía.")
        else:
            for r in info["registros"]:
                tiempo_str = minutos_a_horas_minutos(r['minutos'])
                nota_texto = f" - *Nota: {r['nota']}*" if r['nota'] else ""
                st.markdown(f"- **{r['fecha']}**: Trabajaste **{tiempo_str}**{nota_texto}")