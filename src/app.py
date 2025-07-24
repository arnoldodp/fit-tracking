import streamlit as st
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Agregar el directorio src al path
file_path = Path(__file__).resolve()
src_dir = file_path.parent
sys.path.append(str(src_dir))

from login import login_page
from register import register_page
from training import training_page
from metrics import metrics_page
from nutrition import nutrition_page
from dashboard import dashboard_page
from goals import goals_page

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title=os.getenv("APP_NAME", "Fitness Tracker"),
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar el estado de la sesión
if "page" not in st.session_state:
    st.session_state.page = "login"

# Mostrar solo login y registro si no hay usuario autenticado
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.sidebar.title("Acceso")
    opcion = st.sidebar.radio(
        "Selecciona una opción",
        ["Iniciar Sesión", "Registrarse"]
    )
    if opcion == "Iniciar Sesión":
        login_page()
    else:
        register_page()
    st.stop()

# Usuario autenticado: mostrar la app completa
st.title("Sistema de Seguimiento de Entrenamiento y Nutrición")

# Sidebar con navegación
st.sidebar.title("Navegación")
page = st.sidebar.radio(
    "Ir a",
    ["Dashboard", "Entrenamiento", "Nutrición", "Métricas Corporales", "Metas", "Perfil", "Configuración"]
)

# Botón de cerrar sesión
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.clear()
    st.rerun()

# Contenido principal basado en la página seleccionada
if page == "Dashboard":
    dashboard_page()
    
elif page == "Entrenamiento":
    training_page()
    
elif page == "Nutrición":
    nutrition_page()
    
elif page == "Métricas Corporales":
    metrics_page()
    
elif page == "Metas":
    goals_page()
    
elif page == "Perfil":
    from profile import profile_page
    profile_page()
    
elif page == "Recuperar Contraseña":
    from login import recover_password_page
    recover_password_page()
    
elif page == "Configuración":
    st.header("Configuración")
    st.write("Configura tus preferencias") 