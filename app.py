import random
import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Simulador de Conducción Pro Gamer 2", page_icon="🏎️", layout="wide"
)
st.markdown(
    """
    <style>
    .track-view {
        background-color: #1a252f;
        border: 4px solid #f1c40f;
        border-radius: 10px;
        padding: 20px;
        font-family: monospace;
        font-size: 28px;
        color: #ecf0f1;
        text-align: center;
        letter-spacing: 6px;
        line-height: 1.4;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Estado del juego
if "running" not in st.session_state:
    st.session_state.running = False
if "speed" not in st.session_state:
    st.session_state.speed = 60.0
if "distance" not in st.session_state:
    st.session_state.distance = 0.0
if "gear" not in st.session_state:
    st.session_state.gear = 2
if "car_pos" not in st.session_state:
    st.session_state.car_pos = 1  # 0: Izq, 1: Centro, 2: Der
if "obstacle_pos" not in st.session_state:
    st.session_state.obstacle_pos = random.randint(0, 2)
if "obstacle_row" not in st.session_state:
    st.session_state.obstacle_row = 0
if "crashes" not in st.session_state:
    st.session_state.crashes = 0
if "telemetry" not in st.session_state:
    st.session_state.telemetry = []

st.title("🏎️ Speed Racer: Simulador Automático & Telemetría")
st.caption("Modo de conducción automática en tiempo real con Streamlit")

# Sidebar
st.sidebar.header("⚙️ Garaje & Configuración")
car_type = st.sidebar.selectbox(
    "Selecciona tu Vehículo:",
    [
        "🏎️ Fórmula 1 (Alta velocidad)",
        "🚗 Deportivo (Equilibrado)",
        "🛻 4x4 Off-Road (Resistente)",
    ],
)

if "Fórmula 1" in car_type:
    max_speed, accel_power = 320, 20
elif "Deportivo" in car_type:
    max_speed, accel_power = 240, 15
else:
    max_speed, accel_power = 180, 10

st.sidebar.markdown("---")
st.sidebar.write(f"• Vel. Máxima: **{max_speed} km/h**")

if st.sidebar.button("🔄 Reiniciar Carrera"):
    st.session_state.running = False
    st.session_state.speed = 60.0
    st.session_state.distance = 0.0
    st.session_state.gear = 2
    st.session_state.car_pos = 1
    st.session_state.obstacle_row = 0
    st.session_state.obstacle_pos = random.randint(0, 2)
    st.session_state.crashes = 0
    st.session_state.telemetry = []
    st.rerun()

# Layout
col_controls, col_track = st.columns([1, 2])

with col_controls:
    st.subheader("🎮 Controles del Piloto")

    # Botón Encendido / Apagado del Motor
    if not st.session_state.running:
        if st.button("🔑 ARRANCAR MOTOR", use_container_width=True):
            st.session_state.running = True
            st.rerun()
    else:
        if st.button("🛑 APAGAR MOTOR", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    st.write("---")
    st.write("**Dirección (Cambio de Carril):**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ Izq", use_container_width=True):
            if st.session_state.car_pos > 0:
                st.session_state.car_pos -= 1
    with c2:
        carriles_nom = ["Izquierda", "Centro", "Derecha"]
        st.markdown(
            f"<h5 style='text-align:center;'>{carriles_nom[st.session_state.car_pos]}</h5>",
            unsafe_allow_html=True,
        )
    with c3:
        if st.button("Der ➡️", use_container_width=True):
            if st.session_state.car_pos < 2:
                st.session_state.car_pos += 1

    st.write("---")
    st.write("**Ajuste de Velocidad:**")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("🟢 Más Vel (+20)", use_container_width=True):
            if st.session_state.speed < max_speed:
                st.session_state.speed += accel_power
    with col_a2:
        if st.button("🔴 Menos Vel (-20)", use_container_width=True):
            st.session_state.speed = max(20.0, st.session_state.speed - 20.0)

    st.session_state.gear = min(
        6, max(1, int(st.session_state.speed // 40) + 1)
    )

with col_track:
    st.subheader("🛣️ Vista de la Pista (En Vivo)")

    # Construir matriz de pista de 5 filas x 3 columnas
    grid = [[" | ", " | ", " | "] for _ in range(5)]

    # Colocar obstáculo
    if 0 <= st.session_state.obstacle_row <= 4:
        grid[st.session_state.obstacle_row][st.session_state.obstacle_pos] = (
            " 🔴 "
        )

    # Colocar carro
    car_icon = "🏎️" if "Fórmula" in car_type else "🚗"
    grid[4][st.session_state.car_pos] = f" {car_icon} "

    track_str = "<br>".join(["".join(row) for row in grid])
    st.markdown(
        f'<div class="track-view">{track_str}</div>', unsafe_allow_html=True
    )

    st.write("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Velocidad", f"{st.session_state.speed:.0f} km/h")
    m2.metric("Marcha", f"Nivel {st.session_state.gear}")
    m3.metric("Recorrido", f"{st.session_state.distance:.1f} m")
    m4.metric("Choques", f"{st.session_state.crashes}")

st.write("---")
st.subheader("📈 Telemetría de Conducción")
if len(st.session_state.telemetry) > 0:
    df_telemetry = pd.DataFrame(st.session_state.telemetry)
    st.line_chart(
        df_telemetry,
        x="Distancia (m)",
        y="Velocidad (km/h)",
        color="#f1c40f",
    )

# --- BUCLE DE MOVIMIENTO AUTOMÁTICO ---
if st.session_state.running:
    # Avanzar distancia y obstáculo
    st.session_state.distance += st.session_state.speed / 10
    st.session_state.obstacle_row += 1

    # Detección de colisión / reinicio de obstáculo
    if st.session_state.obstacle_row > 4:
        if st.session_state.car_pos == st.session_state.obstacle_pos:
            st.session_state.crashes += 1
            st.toast("💥 ¡COLISIÓN DETECTADA!", icon="🚨")

        st.session_state.obstacle_row = 0
        st.session_state.obstacle_pos = random.randint(0, 2)

    # Guardar telemetría
    st.session_state.telemetry.append(
        {
            "Distancia (m)": round(st.session_state.distance, 1),
            "Velocidad (km/h)": st.session_state.speed,
        }
    )

    # Calcular delay según la velocidad (a más velocidad, refresco más rápido)
    delay = max(0.15, 0.6 - (st.session_state.speed / 500))
    time.sleep(delay)
    st.rerun()