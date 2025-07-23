import streamlit as st
from datetime import datetime
from database.database import SessionLocal
from models.bodymetric import BodyMetric
import pandas as pd

def metrics_page():
    st.title("Métricas Corporales")
    # Estado para edición
    if "edit_metric_id" not in st.session_state:
        st.session_state.edit_metric_id = None
    # Formulario para registrar nueva métrica
    st.header("Registrar Nueva Métrica Corporal")
    st.markdown("Registra tu peso y altura para calcular el IMC y llevar tu progreso.")
    with st.form("metrics_form"):
        date = st.date_input("Fecha", datetime.now())
        weight = st.number_input("Peso (kg)", min_value=1.0, value=70.0, step=0.1, help="Peso actual en kilogramos.")
        height = st.number_input("Altura (cm)", min_value=50.0, value=170.0, step=0.1, help="Altura actual en centímetros.")
        submit = st.form_submit_button("Guardar Métrica")
        if submit:
            if not weight or not height:
                st.error("Debes ingresar peso y altura.")
            else:
                bmi = round(weight / ((height / 100) ** 2), 2)
                try:
                    db = SessionLocal()
                    new_metric = BodyMetric(
                        user_id=st.session_state.user_id,
                        date=date,
                        weight=weight,
                        height=height,
                        bmi=bmi
                    )
                    db.add(new_metric)
                    db.commit()
                    st.success(f"Métrica registrada exitosamente. IMC: {bmi}")
                except Exception as e:
                    db.rollback()
                    st.error(f"Error al guardar la métrica: {str(e)}")
                finally:
                    db.close()
    # Mostrar historial de métricas
    st.header("Historial de Métricas Corporales")
    # Filtros
    with st.expander("Filtros de búsqueda"):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Fecha inicio", value=None, key="start_metric_date")
        with col2:
            end_date = st.date_input("Fecha fin", value=None, key="end_metric_date")
    db = SessionLocal()
    try:
        query = db.query(BodyMetric).filter(BodyMetric.user_id == st.session_state.user_id)
        if start_date:
            query = query.filter(BodyMetric.date >= start_date)
        if end_date:
            query = query.filter(BodyMetric.date <= end_date)
        metrics = query.order_by(BodyMetric.date.desc()).all()
        if metrics:
            for m in metrics:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{m.date.strftime('%Y-%m-%d')} | Peso: {m.weight} kg | Altura: {m.height} cm | IMC: {m.bmi}")
                with col2:
                    if st.button(f"Editar", key=f"edit_metric_{m.id}"):
                        st.session_state.edit_metric_id = m.id
                    if st.button(f"Eliminar", key=f"delete_metric_{m.id}"):
                        try:
                            db.delete(m)
                            db.commit()
                            st.success("Métrica eliminada exitosamente!")
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error al eliminar la métrica: {str(e)}")
            # Formulario de edición
            if st.session_state.edit_metric_id:
                metric = db.query(BodyMetric).filter(BodyMetric.id == st.session_state.edit_metric_id).first()
                if metric:
                    with st.form("edit_metric_form"):
                        date = st.date_input("Fecha", value=metric.date)
                        weight = st.number_input("Peso (kg)", min_value=1.0, value=metric.weight, step=0.1)
                        height = st.number_input("Altura (cm)", min_value=50.0, value=metric.height, step=0.1)
                        submit = st.form_submit_button("Actualizar Métrica")
                        cancel = st.form_submit_button("Cancelar")
                        if submit:
                            try:
                                metric.date = date
                                metric.weight = weight
                                metric.height = height
                                metric.bmi = round(weight / ((height / 100) ** 2), 2)
                                db.commit()
                                st.success("Métrica actualizada exitosamente!")
                                st.session_state.edit_metric_id = None
                            except Exception as e:
                                db.rollback()
                                st.error(f"Error al actualizar la métrica: {str(e)}")
                        if cancel:
                            st.session_state.edit_metric_id = None
            # Tabla y gráfico
            data = [{
                "Fecha": m.date.strftime('%Y-%m-%d'),
                "Peso (kg)": m.weight,
                "Altura (cm)": m.height,
                "IMC": m.bmi
            } for m in metrics]
            df = pd.DataFrame(data)
            st.dataframe(df)
            st.subheader("Evolución de Peso e IMC")
            st.line_chart(df.set_index("Fecha")[ ["Peso (kg)", "IMC"] ])
        else:
            st.info("No hay métricas registradas para los filtros seleccionados.")
    finally:
        db.close()

if __name__ == "__main__":
    metrics_page() 