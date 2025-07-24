import streamlit as st
from database.database import SessionLocal
from models.user import User
from utils.password import hash_password, verify_password
from datetime import datetime, timedelta
import re

def is_valid_email(email: str) -> bool:
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def check_session():
    if "user_id" not in st.session_state or st.session_state.user_id is None:
        st.error("Sesión no válida. Por favor, inicia sesión nuevamente.")
        st.stop()
    # Expiración por inactividad (5 minutos)
    now = datetime.now()
    if "last_active" in st.session_state:
        if (now - st.session_state.last_active) > timedelta(minutes=5):
            st.session_state.clear()
            st.error("Sesión expirada por inactividad. Por favor, inicia sesión nuevamente.")
            st.stop()
    st.session_state.last_active = now

def profile_page():
    check_session()
    st.title("Perfil de Usuario")
    db = SessionLocal()
    user = db.query(User).filter(User.id == st.session_state.user_id).first()
    if not user:
        st.error("Usuario no encontrado.")
        db.close()
        return
    st.subheader("Editar información personal")
    with st.form("profile_form"):
        full_name = st.text_input("Nombre completo", value=user.full_name or "")
        email = st.text_input("Correo electrónico", value=user.email)
        submit = st.form_submit_button("Guardar cambios")
        if submit:
            if not is_valid_email(email):
                st.error("El correo electrónico no tiene un formato válido.")
            else:
                # Verificar unicidad de email
                existing = db.query(User).filter(User.email == email, User.id != user.id).first()
                if existing:
                    st.error("El correo electrónico ya está registrado por otro usuario.")
                else:
                    user.full_name = full_name
                    user.email = email
                    db.commit()
                    st.success("Datos actualizados correctamente.")
    st.subheader("Cambiar contraseña")
    with st.form("password_form"):
        current_password = st.text_input("Contraseña actual", type="password")
        new_password = st.text_input("Nueva contraseña", type="password")
        new_password_confirm = st.text_input("Confirmar nueva contraseña", type="password")
        submit_pass = st.form_submit_button("Actualizar contraseña")
        if submit_pass:
            if not verify_password(current_password, user.hashed_password):
                st.error("La contraseña actual es incorrecta.")
            elif len(new_password) < 6:
                st.error("La nueva contraseña debe tener al menos 6 caracteres.")
            elif new_password != new_password_confirm:
                st.error("Las nuevas contraseñas no coinciden.")
            else:
                user.hashed_password = hash_password(new_password)
                db.commit()
                st.success("Contraseña actualizada correctamente.")
    db.close() 