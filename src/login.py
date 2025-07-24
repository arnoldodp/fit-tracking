import streamlit as st
from database.database import SessionLocal
from models.user import User
from utils.password import verify_password, hash_password
import re

def is_valid_email(email: str) -> bool:
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

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
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos. Intenta de nuevo.")
    # Enlace para registro y recuperación
    st.info("¿No tienes una cuenta?")
    if st.button("Registrarse"):
        st.session_state.page = "register"
        st.rerun()
    st.info("¿Olvidaste tu contraseña?")
    if st.button("Recuperar contraseña"):
        st.session_state.page = "recover_password"
        st.rerun()

def authenticate_user(username: str, password: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.hashed_password):
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

def recover_password_page():
    st.title("Recuperar Contraseña")
    st.markdown("Ingresa tu correo electrónico registrado para restablecer tu contraseña.")
    with st.form("recover_form"):
        email = st.text_input("Correo electrónico")
        submit = st.form_submit_button("Enviar instrucciones")
        if submit:
            if not is_valid_email(email):
                st.error("El correo electrónico no tiene un formato válido.")
            else:
                db = SessionLocal()
                user = db.query(User).filter(User.email == email).first()
                if user:
                    st.success("Se ha enviado un enlace de restablecimiento (simulado) a tu correo.")
                    st.info("Por motivos de desarrollo, puedes establecer una nueva contraseña aquí mismo.")
                    with st.form("reset_form"):
                        new_password = st.text_input("Nueva contraseña", type="password")
                        new_password_confirm = st.text_input("Confirmar nueva contraseña", type="password")
                        submit_reset = st.form_submit_button("Restablecer contraseña")
                        if submit_reset:
                            if len(new_password) < 6:
                                st.error("La nueva contraseña debe tener al menos 6 caracteres.")
                            elif new_password != new_password_confirm:
                                st.error("Las contraseñas no coinciden.")
                            else:
                                user.hashed_password = hash_password(new_password)
                                db.commit()
                                st.success("Contraseña restablecida correctamente. Ahora puedes iniciar sesión.")
                                st.session_state.page = "login"
                                st.rerun()
                else:
                    st.error("No se encontró un usuario con ese correo electrónico.")
                db.close()

if __name__ == "__main__":
    login_page() 