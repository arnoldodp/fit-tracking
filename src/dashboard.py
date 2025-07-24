import streamlit as st
from datetime import datetime, timedelta
from database.database import SessionLocal
from models.bodymetric import BodyMetric
from models.meallog import MealLog
from models.food import Food
from models.workout import Workout
import pandas as pd

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

def dashboard_page():
    check_session()
    st.title("Dashboard")
    st.markdown("Bienvenido a tu panel de control. Aquí puedes ver tu progreso y KPIs principales.")
    db = SessionLocal()
    user_id = st.session_state.user_id

    # Peso actual y evolución
    metric = db.query(BodyMetric).filter(BodyMetric.user_id == user_id).order_by(BodyMetric.date.desc()).first()
    if metric:
        st.metric("Peso actual (kg)", f"{metric.weight}", help="Último peso registrado.")
    else:
        st.info("Registra tu peso para ver el progreso.")

    # Calorías consumidas hoy
    today = datetime.now().date()
    meals = db.query(MealLog).filter(MealLog.user_id == user_id, MealLog.date >= today).all()
    foods = {f.id: f for f in db.query(Food).all()}
    total_cal = 0
    for meal in meals:
        food = foods.get(meal.food_id)
        if food:
            total_cal += food.calories * meal.quantity / 100
    st.metric("Calorías consumidas hoy", f"{round(total_cal, 2)} kcal", help="Suma de calorías de todas las comidas de hoy.")

    # Entrenamientos recientes
    st.subheader("Entrenamientos recientes")
    workouts = db.query(Workout).filter(Workout.user_id == user_id).order_by(Workout.date.desc()).limit(5).all()
    if workouts:
        data = [{
            "Fecha": w.date.strftime('%Y-%m-%d'),
            "Nombre": w.name,
            "Duración (min)": w.duration
        } for w in workouts]
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info("No hay entrenamientos registrados aún.")

    # Gráfico de evolución de peso
    st.subheader("Evolución de Peso")
    metrics = db.query(BodyMetric).filter(BodyMetric.user_id == user_id).order_by(BodyMetric.date).all()
    if metrics:
        data = [{"Fecha": m.date.strftime('%Y-%m-%d'), "Peso": m.weight} for m in metrics]
        df = pd.DataFrame(data)
        st.line_chart(df.set_index("Fecha"))
    else:
        st.info("No hay datos de peso para graficar.")

    db.close()

if __name__ == "__main__":
    dashboard_page() 