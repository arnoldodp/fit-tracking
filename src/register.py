import streamlit as st
import re
from database.database import SessionLocal
from models.user import User
from utils.password import hash_password

def is_valid_email(email: str) -> bool:
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def register_page():
    st.title("Registro de Usuario")
    st.markdown("Por favor, completa todos los campos para crear tu cuenta.")
    # Formulario de registro
    with st.form("register_form"):
        username = st.text_input("Usuario", help="Elige un nombre de usuario único.")
        email = st.text_input("Correo Electrónico", help="Introduce un correo válido.")
        full_name = st.text_input("Nombre Completo", help="Tu nombre real o apodo.")
        password = st.text_input("Contraseña", type="password", help="Debe tener al menos 6 caracteres.")
        password_confirm = st.text_input("Confirmar Contraseña", type="password", help="Repite la contraseña.")
        submit = st.form_submit_button("Registrarse")
        if submit:
            if not username or not email or not password or not password_confirm:
                st.error("Todos los campos son obligatorios.")
            elif not is_valid_email(email):
                st.error("El correo electrónico no tiene un formato válido.")
            elif len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            elif password != password_confirm:
                st.error("Las contraseñas no coinciden.")
            else:
                db = SessionLocal()
                existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
                db.close()
                if existing_user:
                    if existing_user.username == username:
                        st.error("El nombre de usuario ya está en uso. Elige otro.")
                    else:
                        st.error("El correo electrónico ya está registrado. Usa otro.")
                else:
                    if register_user(username, email, full_name, password):
                        st.success("¡Registro exitoso! Ahora puedes iniciar sesión.")
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error("Ocurrió un error al registrar el usuario. Intenta de nuevo.")
    # Enlace para inicio de sesión
    st.info("¿Ya tienes una cuenta?")
    if st.button("Iniciar Sesión"):
        st.session_state.page = "login"
        st.rerun()

def register_user(username: str, email: str, full_name: str, password: str) -> bool:
    db = SessionLocal()
    try:
        hashed_password = hash_password(password)
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        st.error(f"Error al registrar usuario: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    register_page() 