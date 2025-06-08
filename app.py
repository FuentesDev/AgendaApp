import streamlit as st
import json
from datetime import datetime, timedelta, date
from pathlib import Path

# --------------------
# Constants and State
# --------------------
DATA_FILE = Path("data.json")
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --------------------
# Helper Functions
# --------------------
def load_data():
    """Carga datos desde archivo JSON o retorna estructura inicial"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"start_date": None, "end_date": None, "weekly_plan": {d: [] for d in WEEKDAYS}, "records": {}}


def save_data(data):
    """Guarda datos en archivo JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def date_range(start: date, end: date):
    """Genera fechas entre start y end inclusive"""
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)

# --------------------
# Cargar datos
# --------------------

data = load_data()

# --------------------
# Sidebar
# --------------------
st.sidebar.title("Control de Entrenamientos")
mode = st.sidebar.radio(
    "Selecciona una opción:",
    ["Configurar fechas", "Configurar semana", "Seguimiento"]
)

# --------------------
# 1) Configurar fechas
# --------------------
if mode == "Configurar fechas":
    st.header("Definir rango de fechas")
    start = st.date_input("Fecha de inicio", value=datetime.today().date())
    end = st.date_input("Fecha de fin", value=datetime.today().date() + timedelta(days=7))
    if st.button("Guardar fechas"):
        if start <= end:
            data['start_date'] = start.isoformat()
            data['end_date'] = end.isoformat()
            save_data(data)
            st.success("Fechas guardadas correctamente.")
        else:
            st.error("Fecha de inicio debe ser anterior o igual a fecha de fin.")

# --------------------
# 2) Configurar semana
# --------------------
elif mode == "Configurar semana":
    st.header("Configurar plan semanal")
    for day in WEEKDAYS:
        txt = st.text_input(
            f"Actividades para {day} (separadas por coma)",
            value=", ".join(data['weekly_plan'].get(day, []))
        )
        data['weekly_plan'][day] = [a.strip() for a in txt.split(",") if a.strip()]
    if st.button("Guardar plan semanal"):
        save_data(data)
        st.success("Plan semanal guardado.")

# --------------------
# 3) Seguimiento diario
# --------------------
elif mode == "Seguimiento":
    st.header("Seguimiento de actividades")
    if not data['start_date'] or not data['end_date']:
        st.warning("Primero configura las fechas.")
    else:
        start = date.fromisoformat(data['start_date'])
        end = date.fromisoformat(data['end_date'])
        sel = st.date_input("Selecciona día", value=start, min_value=start, max_value=end)
        day = sel.strftime("%A")
        acts = data['weekly_plan'].get(day, [])
        if not acts:
            st.info("Sin actividades para este día.")
        else:
            done_list = data['records'].get(sel.isoformat(), [])
            new_done = []
            for act in acts:
                if st.checkbox(act, value=(act in done_list)):
                    new_done.append(act)
            data['records'][sel.isoformat()] = new_done
            if st.button("Guardar seguimiento"):
                save_data(data)
                st.success("Seguimiento guardado.")

# --------------------
# 4) Vista principal: Hoy
# --------------------
else:
    st.title("🏋️‍♂️ Hoy")
    if data['start_date'] and data['end_date']:
        today = datetime.today().date()
        start = date.fromisoformat(data['start_date'])
        end = date.fromisoformat(data['end_date'])
        if start <= today <= end:
            day = today.strftime("%A")
            pend = [a for a in data['weekly_plan'].get(day, [])
                    if a not in data['records'].get(today.isoformat(), [])]
            st.write(f"Pendientes para {today}:")
            for act in pend:
                if st.checkbox(act, key=f"today_{act}"):
                    data['records'].setdefault(today.isoformat(), []).append(act)
                    save_data(data)
                    st.experimental_rerun()
        else:
            st.info("Hoy está fuera del rango configurado.")
    else:
        st.info("Configura primero las fechas en el menú lateral.")

# --------------------
# Exportar/Importar JSON
# --------------------
st.sidebar.header("Backup")
col1, col2 = st.sidebar.columns(2)
if col1.button("Descargar JSON"):
    st.sidebar.download_button(
        "Descargar datos", data=json.dumps(data, indent=4, ensure_ascii=False),
        file_name="plan.json", mime="application/json"
    )
if col2.button("Cargar JSON"):
    up = st.sidebar.file_uploader("Selecciona JSON", type="json")
    if up:
        new = json.load(up)
        data.update(new)
        save_data(data)
        st.sidebar.success("Datos importados.")
