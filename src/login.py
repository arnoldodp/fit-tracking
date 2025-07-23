import streamlit as st
import bcrypt
from database.database import SessionLocal
from models.user import User

def login_page():
    st.title("Iniciar Sesión")
    st.markdown("Accede con tu usuario y contraseña registrados.")
    # Formulario de inicio de sesión
    with st.form("login_form"):
        username = st.text_input("Usuario", help="Tu nombre de usuario registrado.")
        password = st.text_input("Contraseña", type="password", help="Tu contraseña secreta.")
        submit = st.form_submit_button("Iniciar Sesión")
        if submit:
            if not username or not password:
                st.error("Debes ingresar usuario y contraseña.")
            elif authenticate_user(username, password):
                st.success("¡Inicio de sesión exitoso!")
                st.session_state.user_id = get_user_id(username)
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos. Intenta de nuevo.")
    # Enlace para registro
    st.info("¿No tienes una cuenta?")
    if st.button("Registrarse"):
        st.session_state.page = "register"
        st.experimental_rerun()

def authenticate_user(username: str, password: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            return True
        return False
    finally:
        db.close()

def get_user_id(username: str) -> int:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        return user.id if user else None
    finally:
        db.close()

if __name__ == "__main__":
    login_page() 