import streamlit as st
from datetime import date
from src.database.database import SessionLocal
from src.models.goal import Goal
import pandas as pd

def goals_page():
    st.title("Metas y Objetivos")
    db = SessionLocal()
    user_id = st.session_state.user_id

    # Formulario para crear/editar meta
    if "edit_goal_id" not in st.session_state:
        st.session_state.edit_goal_id = None
    st.header("Crear Nueva Meta")
    with st.form("goal_form"):
        if st.session_state.edit_goal_id:
            goal = db.query(Goal).filter(Goal.id == st.session_state.edit_goal_id).first()
            title = st.text_input("Título de la meta", value=goal.title)
            description = st.text_area("Descripción", value=goal.description or "")
            category = st.selectbox("Categoría", ["weight", "nutrition", "exercise"], index=["weight", "nutrition", "exercise"].index(goal.category))
            target_value = st.number_input("Valor objetivo", value=goal.target_value or 0.0)
            target_unit = st.text_input("Unidad objetivo", value=goal.target_unit or "kg")
            start_date = st.date_input("Fecha de inicio", value=goal.start_date)
            target_date = st.date_input("Fecha objetivo", value=goal.target_date or date.today())
            submit = st.form_submit_button("Actualizar Meta")
            cancel = st.form_submit_button("Cancelar")
            if submit:
                goal.title = title
                goal.description = description
                goal.category = category
                goal.target_value = target_value
                goal.target_unit = target_unit
                goal.start_date = start_date
                goal.target_date = target_date
                db.commit()
                st.success("Meta actualizada exitosamente!")
                st.session_state.edit_goal_id = None
            if cancel:
                st.session_state.edit_goal_id = None
        else:
            title = st.text_input("Título de la meta")
            description = st.text_area("Descripción")
            category = st.selectbox("Categoría", ["weight", "nutrition", "exercise"])
            target_value = st.number_input("Valor objetivo", value=0.0)
            target_unit = st.text_input("Unidad objetivo", value="kg")
            start_date = st.date_input("Fecha de inicio", value=date.today())
            target_date = st.date_input("Fecha objetivo", value=date.today())
            submit = st.form_submit_button("Crear Meta")
            if submit:
                new_goal = Goal(
                    user_id=user_id,
                    title=title,
                    description=description,
                    category=category,
                    target_value=target_value,
                    target_unit=target_unit,
                    start_date=start_date,
                    target_date=target_date,
                    completed=False
                )
                db.add(new_goal)
                db.commit()
                st.success("Meta creada exitosamente!")
    # Listado de metas
    st.header("Metas Activas")
    goals = db.query(Goal).filter(Goal.user_id == user_id, Goal.completed == False).order_by(Goal.target_date).all()
    if goals:
        for g in goals:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{g.title}** | {g.category} | Objetivo: {g.target_value} {g.target_unit} para {g.target_date}")
                if g.description:
                    st.caption(g.description)
            with col2:
                if st.button(f"Editar", key=f"edit_goal_{g.id}"):
                    st.session_state.edit_goal_id = g.id
                if st.button(f"Completar", key=f"complete_goal_{g.id}"):
                    g.completed = True
                    g.completed_date = date.today()
                    db.commit()
                    st.success("Meta marcada como completada!")
                if st.button(f"Eliminar", key=f"delete_goal_{g.id}"):
                    db.delete(g)
                    db.commit()
                    st.success("Meta eliminada!")
        # Tabla resumen
        data = [{
            "Título": g.title,
            "Categoría": g.category,
            "Objetivo": f"{g.target_value} {g.target_unit}",
            "Fecha objetivo": g.target_date,
            "Estado": "Completada" if g.completed else "Activa"
        } for g in goals]
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info("No tienes metas activas.")
    # Metas completadas
    st.header("Metas Completadas")
    completed_goals = db.query(Goal).filter(Goal.user_id == user_id, Goal.completed == True).order_by(Goal.completed_date.desc()).all()
    if completed_goals:
        data = [{
            "Título": g.title,
            "Categoría": g.category,
            "Objetivo": f"{g.target_value} {g.target_unit}",
            "Fecha objetivo": g.target_date,
            "Completada en": g.completed_date
        } for g in completed_goals]
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info("No tienes metas completadas aún.")
    db.close()

if __name__ == "__main__":
    goals_page() 