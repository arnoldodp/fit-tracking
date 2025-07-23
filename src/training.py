import streamlit as st
from datetime import datetime
from database.database import SessionLocal
from models.exercise import Exercise, MuscleGroup
from models.workout import Workout, WorkoutExercise
import pandas as pd

def training_page():
    st.title("Registro de Entrenamiento")
    
    tab1, tab2, tab3 = st.tabs(["Registrar Entrenamiento", "Historial", "Ejercicios"])
    
    with tab1:
        register_workout()
    with tab2:
        show_workout_history()
    with tab3:
        manage_exercises()

def register_workout():
    st.header("Registrar Nuevo Entrenamiento")
    st.markdown("Completa los datos para registrar tu sesión de entrenamiento.")
    with st.form("workout_form"):
        workout_name = st.text_input("Nombre del Entrenamiento", help="Ejemplo: Full Body, Piernas, Pecho-Espalda...")
        workout_date = st.date_input("Fecha", datetime.now())
        duration = st.number_input("Duración (minutos)", min_value=1, value=60, help="Duración total del entrenamiento.")
        notes = st.text_area("Notas", help="Observaciones, sensaciones, etc. (opcional)")
        db = SessionLocal()
        exercises = db.query(Exercise).all()
        db.close()
        if not exercises:
            st.warning("No hay ejercicios disponibles. Agrega algunos en la pestaña 'Ejercicios'.")
            st.form_submit_button("Guardar Entrenamiento", disabled=True)
            return
        exercise_containers = []
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                exercise_id = st.selectbox(
                    "Ejercicio",
                    options=[e.id for e in exercises],
                    format_func=lambda x: next((e.name for e in exercises if e.id == x), ""),
                    key=f"exercise_0",
                    help="Selecciona el ejercicio realizado."
                )
            with col2:
                sets = st.number_input("Series", min_value=1, value=3, key=f"sets_0", help="Número de series.")
            with col3:
                reps = st.number_input("Repeticiones", min_value=1, value=12, key=f"reps_0", help="Repeticiones por serie.")
            with col4:
                weight = st.number_input("Peso (kg)", min_value=0.0, value=0.0, key=f"weight_0", help="Peso utilizado en kg.")
            exercise_containers.append({
                "exercise_id": exercise_id,
                "sets": sets,
                "reps": reps,
                "weight": weight
            })
        if st.form_submit_button("Guardar Entrenamiento"):
            if not workout_name:
                st.error("Por favor ingresa un nombre para el entrenamiento.")
                return
            try:
                db = SessionLocal()
                new_workout = Workout(
                    user_id=st.session_state.user_id,
                    name=workout_name,
                    date=workout_date,
                    duration=duration,
                    notes=notes
                )
                db.add(new_workout)
                db.flush()
                for exercise_data in exercise_containers:
                    workout_exercise = WorkoutExercise(
                        workout_id=new_workout.id,
                        exercise_id=exercise_data["exercise_id"],
                        sets=exercise_data["sets"],
                        reps=exercise_data["reps"],
                        weight=exercise_data["weight"]
                    )
                    db.add(workout_exercise)
                db.commit()
                st.success("Entrenamiento registrado exitosamente!")
            except Exception as e:
                db.rollback()
                st.error(f"Error al guardar el entrenamiento: {str(e)}")
            finally:
                db.close()

def show_workout_history():
    st.header("Historial de Entrenamientos")
    if "edit_workout_id" not in st.session_state:
        st.session_state.edit_workout_id = None
    # Filtros
    with st.expander("Filtros de búsqueda"):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Fecha inicio", value=None, key="start_date")
        with col2:
            end_date = st.date_input("Fecha fin", value=None, key="end_date")
        search_name = st.text_input("Buscar por nombre de entrenamiento", help="Ejemplo: Full Body, Piernas...")
    db = SessionLocal()
    try:
        query = db.query(Workout).filter(Workout.user_id == st.session_state.user_id)
        if start_date:
            query = query.filter(Workout.date >= start_date)
        if end_date:
            query = query.filter(Workout.date <= end_date)
        if search_name:
            query = query.filter(Workout.name.ilike(f"%{search_name}%"))
        workouts = query.order_by(Workout.date.desc()).all()
        if not workouts:
            st.info("No hay entrenamientos registrados para los filtros seleccionados.")
            return
        for workout in workouts:
            with st.expander(f"{workout.date.strftime('%Y-%m-%d')} - {workout.name}"):
                st.write(f"Duración: {workout.duration} minutos")
                if workout.notes:
                    st.write(f"Notas: {workout.notes}")
                workout_exercises = db.query(WorkoutExercise).filter(
                    WorkoutExercise.workout_id == workout.id
                ).join(Exercise).all()
                if workout_exercises:
                    data = []
                    for we in workout_exercises:
                        data.append({
                            "Ejercicio": we.exercise.name,
                            "Series": we.sets,
                            "Repeticiones": we.reps,
                            "Peso (kg)": we.weight
                        })
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Editar", key=f"edit_{workout.id}"):
                        st.session_state.edit_workout_id = workout.id
                with col2:
                    if st.button(f"Eliminar", key=f"delete_{workout.id}"):
                        try:
                            db.delete(workout)
                            db.commit()
                            st.success("Entrenamiento eliminado exitosamente!")
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error al eliminar el entrenamiento: {str(e)}")
        # Formulario de edición
        if st.session_state.edit_workout_id:
            workout = db.query(Workout).filter(Workout.id == st.session_state.edit_workout_id).first()
            if workout:
                with st.form("edit_workout_form"):
                    name = st.text_input("Nombre del Entrenamiento", value=workout.name)
                    date = st.date_input("Fecha", value=workout.date)
                    duration = st.number_input("Duración (minutos)", min_value=1, value=workout.duration or 60)
                    notes = st.text_area("Notas", value=workout.notes or "")
                    submit = st.form_submit_button("Actualizar Entrenamiento")
                    cancel = st.form_submit_button("Cancelar")
                    if submit:
                        try:
                            workout.name = name
                            workout.date = date
                            workout.duration = duration
                            workout.notes = notes
                            db.commit()
                            st.success("Entrenamiento actualizado exitosamente!")
                            st.session_state.edit_workout_id = None
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error al actualizar el entrenamiento: {str(e)}")
                    if cancel:
                        st.session_state.edit_workout_id = None
    finally:
        db.close()

def manage_exercises():
    st.header("Gestión de Ejercicios")
    with st.form("exercise_form"):
        st.subheader("Agregar Nuevo Ejercicio")
        name = st.text_input("Nombre del Ejercicio")
        muscle_group = st.selectbox(
            "Grupo Muscular",
            options=[group.value for group in MuscleGroup]
        )
        description = st.text_area("Descripción")
        instructions = st.text_area("Instrucciones")
        video_url = st.text_input("URL del Video (opcional)")
        image_url = st.text_input("URL de la Imagen (opcional)")
        if st.form_submit_button("Agregar Ejercicio"):
            if not name or not muscle_group:
                st.error("Por favor completa los campos requeridos")
                return
            try:
                db = SessionLocal()
                new_exercise = Exercise(
                    name=name,
                    muscle_group=muscle_group,
                    description=description,
                    instructions=instructions,
                    video_url=video_url,
                    image_url=image_url
                )
                db.add(new_exercise)
                db.commit()
                st.success("Ejercicio agregado exitosamente!")
            except Exception as e:
                db.rollback()
                st.error(f"Error al agregar el ejercicio: {str(e)}")
            finally:
                db.close()
    db = SessionLocal()
    exercises = db.query(Exercise).all()
    db.close()
    if exercises:
        data = []
        for exercise in exercises:
            data.append({
                "Nombre": exercise.name,
                "Grupo Muscular": exercise.muscle_group.value,
                "Descripción": exercise.description or ""
            })
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info("No hay ejercicios registrados aún.")

if __name__ == "__main__":
    training_page() 