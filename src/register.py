import streamlit as st
import bcrypt
from database.database import SessionLocal
from models.user import User

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
            elif len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            elif password != password_confirm:
                st.error("Las contraseñas no coinciden.")
            else:
                if register_user(username, email, full_name, password):
                    st.success("¡Registro exitoso! Ahora puedes iniciar sesión.")
                    st.session_state.page = "login"
                    st.experimental_rerun()
                else:
                    st.error("El usuario o correo electrónico ya existe. Prueba con otros datos.")
    
    # Enlace para inicio de sesión
    st.info("¿Ya tienes una cuenta?")
    if st.button("Iniciar Sesión"):
        st.session_state.page = "login"
        st.experimental_rerun()

def register_user(username: str, email: str, full_name: str, password: str) -> bool:
    db = SessionLocal()
    try:
        # Verificar si el usuario o email ya existe
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            return False
        # Crear el hash de la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Crear nuevo usuario
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password.decode('utf-8')
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