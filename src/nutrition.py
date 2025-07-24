import streamlit as st
from datetime import datetime, timedelta
from database.database import SessionLocal
from models.food import Food
from models.meallog import MealLog
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

def nutrition_page():
    check_session()
    st.title("Registro de Nutrición")
    
    tab1, tab2, tab3 = st.tabs(["Registrar Comida", "Historial", "Alimentos"])
    
    with tab1:
        register_meal()
    with tab2:
        show_meal_history()
    with tab3:
        manage_foods()

def register_meal():
    st.header("Registrar Nueva Comida")
    st.markdown("Registra lo que has comido para llevar el control de tus calorías.")
    db = SessionLocal()
    foods = db.query(Food).all()
    db.close()
    if not foods:
        st.warning("No hay alimentos registrados. Agrega algunos en la pestaña 'Alimentos'.")
        return
    with st.form("meal_form"):
        date = st.date_input("Fecha", datetime.now())
        food_id = st.selectbox(
            "Alimento",
            options=[f.id for f in foods],
            format_func=lambda x: next((f.name for f in foods if f.id == x), ""),
            help="Selecciona el alimento consumido."
        )
        quantity = st.number_input("Cantidad (gramos)", min_value=1.0, value=100.0, step=1.0, help="Cantidad en gramos.")
        submit = st.form_submit_button("Registrar Comida")
        if submit:
            if not quantity or not food_id:
                st.error("Debes seleccionar un alimento y la cantidad.")
            else:
                try:
                    db = SessionLocal()
                    new_meal = MealLog(
                        user_id=st.session_state.user_id,
                        food_id=food_id,
                        date=date,
                        quantity=quantity
                    )
                    db.add(new_meal)
                    db.commit()
                    st.success("Comida registrada exitosamente!")
                except Exception as e:
                    db.rollback()
                    st.error(f"Error al registrar la comida: {str(e)}")
                finally:
                    db.close()

def show_meal_history():
    st.header("Historial de Comidas")
    if "edit_meal_id" not in st.session_state:
        st.session_state.edit_meal_id = None
    # Filtros
    with st.expander("Filtros de búsqueda"):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Fecha inicio", value=None, key="start_meal_date")
        with col2:
            end_date = st.date_input("Fecha fin", value=None, key="end_meal_date")
        search_food = st.text_input("Buscar por alimento", help="Ejemplo: Pollo, Manzana...")
    db = SessionLocal()
    try:
        meals_query = db.query(MealLog).filter(MealLog.user_id == st.session_state.user_id)
        foods = {f.id: f for f in db.query(Food).all()}
        if start_date:
            meals_query = meals_query.filter(MealLog.date >= start_date)
        if end_date:
            meals_query = meals_query.filter(MealLog.date <= end_date)
        if search_food:
            food_ids = [fid for fid, f in foods.items() if search_food.lower() in f.name.lower()]
            meals_query = meals_query.filter(MealLog.food_id.in_(food_ids))
        meals = meals_query.order_by(MealLog.date.desc()).all()
        if not meals:
            st.info("No hay comidas registradas para los filtros seleccionados.")
            return
        data = []
        for meal in meals:
            food = foods.get(meal.food_id)
            if food:
                cal = round(food.calories * meal.quantity / 100, 2)
                prot = round((food.protein or 0) * meal.quantity / 100, 2)
                carb = round((food.carbs or 0) * meal.quantity / 100, 2)
                fat = round((food.fat or 0) * meal.quantity / 100, 2)
                data.append({
                    "Fecha": meal.date.strftime('%Y-%m-%d'),
                    "Alimento": food.name,
                    "Cantidad (g)": meal.quantity,
                    "Calorías": cal,
                    "Proteína": prot,
                    "Carbohidratos": carb,
                    "Grasas": fat
                })
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.subheader("Calorías totales por día")
        if not df.empty:
            resumen = df.groupby("Fecha")["Calorías"].sum().reset_index()
            st.bar_chart(resumen.set_index("Fecha"))
            # Gráficos de macronutrientes
            st.subheader("Distribución de Macronutrientes por Día")
            macro = df.groupby("Fecha")[["Proteína", "Carbohidratos", "Grasas"]].sum()
            st.bar_chart(macro)
            st.subheader("Distribución porcentual de macronutrientes (último día registrado)")
            last_day = df["Fecha"].max()
            macro_last = df[df["Fecha"] == last_day][["Proteína", "Carbohidratos", "Grasas"]].sum()
            st.write(f"Fecha: {last_day}")
            st.plotly_chart(
                __import__('plotly.express').pie(
                    names=["Proteína", "Carbohidratos", "Grasas"],
                    values=macro_last.values,
                    title="Distribución porcentual de macronutrientes"
                ),
                use_container_width=True
            )
    finally:
        db.close()

def manage_foods():
    st.header("Gestión de Alimentos")
    st.markdown("Agrega, edita o elimina alimentos para llevar un control preciso de tu dieta.")
    # Estado para edición
    if "edit_food_id" not in st.session_state:
        st.session_state.edit_food_id = None
    db = SessionLocal()
    foods = db.query(Food).all()
    db.close()
    # Formulario para agregar o editar alimento
    with st.form("food_form"):
        if st.session_state.edit_food_id:
            db = SessionLocal()
            food = db.query(Food).filter(Food.id == st.session_state.edit_food_id).first()
            db.close()
            name = st.text_input("Nombre del Alimento", value=food.name)
            calories = st.number_input("Calorías por 100g", min_value=0.0, value=food.calories, step=1.0)
            protein = st.number_input("Proteína (g/100g)", min_value=0.0, value=food.protein or 0.0, step=0.1)
            carbs = st.number_input("Carbohidratos (g/100g)", min_value=0.0, value=food.carbs or 0.0, step=0.1)
            fat = st.number_input("Grasas (g/100g)", min_value=0.0, value=food.fat or 0.0, step=0.1)
            submit = st.form_submit_button("Actualizar Alimento")
            cancel = st.form_submit_button("Cancelar")
            if submit:
                try:
                    db = SessionLocal()
                    food.name = name
                    food.calories = calories
                    food.protein = protein
                    food.carbs = carbs
                    food.fat = fat
                    db.commit()
                    st.success("Alimento actualizado exitosamente!")
                    st.session_state.edit_food_id = None
                except Exception as e:
                    db.rollback()
                    st.error(f"Error al actualizar el alimento: {str(e)}")
                finally:
                    db.close()
            if cancel:
                st.session_state.edit_food_id = None
        else:
            name = st.text_input("Nombre del Alimento")
            calories = st.number_input("Calorías por 100g", min_value=0.0, value=100.0, step=1.0)
            protein = st.number_input("Proteína (g/100g)", min_value=0.0, value=0.0, step=0.1)
            carbs = st.number_input("Carbohidratos (g/100g)", min_value=0.0, value=0.0, step=0.1)
            fat = st.number_input("Grasas (g/100g)", min_value=0.0, value=0.0, step=0.1)
            submit = st.form_submit_button("Agregar Alimento")
            if submit:
                if not name:
                    st.error("El nombre es obligatorio")
                else:
                    try:
                        db = SessionLocal()
                        new_food = Food(
                            name=name,
                            calories=calories,
                            protein=protein,
                            carbs=carbs,
                            fat=fat
                        )
                        db.add(new_food)
                        db.commit()
                        st.success("Alimento agregado exitosamente!")
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error al agregar el alimento: {str(e)}")
                    finally:
                        db.close()
    # Mostrar alimentos existentes con opciones de editar/eliminar
    db = SessionLocal()
    foods = db.query(Food).all()
    db.close()
    if foods:
        data = []
        for f in foods:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{f.name}** | Calorías: {f.calories} | Prot: {f.protein} | Carb: {f.carbs} | Grasa: {f.fat}")
            with col2:
                if st.button(f"Editar", key=f"edit_{f.id}"):
                    st.session_state.edit_food_id = f.id
                if st.button(f"Eliminar", key=f"delete_{f.id}"):
                    try:
                        db = SessionLocal()
                        db.delete(db.query(Food).filter(Food.id == f.id).first())
                        db.commit()
                        st.success("Alimento eliminado exitosamente!")
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error al eliminar el alimento: {str(e)}")
                    finally:
                        db.close()
        # Mostrar tabla resumen
        data = [{
            "Nombre": f.name,
            "Calorías": f.calories,
            "Proteína": f.protein,
            "Carbohidratos": f.carbs,
            "Grasas": f.fat
        } for f in foods]
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info("No hay alimentos registrados aún.")

if __name__ == "__main__":
    nutrition_page() 