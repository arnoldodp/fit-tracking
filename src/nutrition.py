import streamlit as st
from datetime import datetime
from database.database import SessionLocal
from models.food import Food
from models.meallog import MealLog
import pandas as pd

def nutrition_page():
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
        for meal in meals:
            food = foods.get(meal.food_id)
            if food:
                cal = round(food.calories * meal.quantity / 100, 2)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{meal.date.strftime('%Y-%m-%d')} | {food.name} | {meal.quantity}g | {cal} kcal")
                with col2:
                    if st.button(f"Editar", key=f"edit_meal_{meal.id}"):
                        st.session_state.edit_meal_id = meal.id
                    if st.button(f"Eliminar", key=f"delete_meal_{meal.id}"):
                        try:
                            db.delete(meal)
                            db.commit()
                            st.success("Comida eliminada exitosamente!")
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error al eliminar la comida: {str(e)}")
        # Formulario de edición
        if st.session_state.edit_meal_id:
            meal = db.query(MealLog).filter(MealLog.id == st.session_state.edit_meal_id).first()
            if meal:
                with st.form("edit_meal_form"):
                    date = st.date_input("Fecha", value=meal.date)
                    food_id = st.selectbox(
                        "Alimento",
                        options=[f.id for f in foods.values()],
                        format_func=lambda x: foods[x].name,
                        index=list(foods.keys()).index(meal.food_id)
                    )
                    quantity = st.number_input("Cantidad (gramos)", min_value=1.0, value=meal.quantity, step=1.0)
                    submit = st.form_submit_button("Actualizar Comida")
                    cancel = st.form_submit_button("Cancelar")
                    if submit:
                        try:
                            meal.date = date
                            meal.food_id = food_id
                            meal.quantity = quantity
                            db.commit()
                            st.success("Comida actualizada exitosamente!")
                            st.session_state.edit_meal_id = None
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error al actualizar la comida: {str(e)}")
                    if cancel:
                        st.session_state.edit_meal_id = None
        # Tabla y gráfico
        data = []
        for meal in meals:
            food = foods.get(meal.food_id)
            if food:
                cal = round(food.calories * meal.quantity / 100, 2)
                data.append({
                    "Fecha": meal.date.strftime('%Y-%m-%d'),
                    "Alimento": food.name,
                    "Cantidad (g)": meal.quantity,
                    "Calorías": cal
                })
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.subheader("Calorías totales por día")
        if not df.empty:
            resumen = df.groupby("Fecha")["Calorías"].sum().reset_index()
            st.bar_chart(resumen.set_index("Fecha"))
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