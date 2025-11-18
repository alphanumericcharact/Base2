import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Sistema de Monitoreo de Gas - Restaurante La Cazuela Antioqueña",
    page_icon="🔥",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title('🔥 Sistema de Monitoreo de Gas - Restaurante La Cazuela Antioqueña')
st.markdown("""
    ### 🏆 Restaurante Tradicional Medellín - El Poblado
    Sistema de monitoreo en tiempo real de los niveles de gas propano para garantizar
    la seguridad y continuidad operativa de nuestra cocina.
""")

# Create map data for the restaurant
restaurant_location = pd.DataFrame({
    'lat': [6.2081],
    'lon': [-75.5675],
    'location': ['Restaurante La Cazuela Antioqueña']
})

# Display map
st.subheader("📍 Ubicación del Restaurante - El Poblado, Medellín")
st.map(restaurant_location, zoom=16)

# File uploader
uploaded_file = st.file_uploader('Cargar datos del sensor de gas (CSV)', type=['csv'])

if uploaded_file is not None:
    try:
        # Load and process data
        df1 = pd.read_csv(uploaded_file)
        
        # Renombrar la columna a 'variable'
        if 'Time' in df1.columns:
            other_columns = [col for col in df1.columns if col != 'Time']
            if len(other_columns) > 0:
                df1 = df1.rename(columns={other_columns[0]: 'variable'})
        else:
            df1 = df1.rename(columns={df1.columns[0]: 'variable'})
        
        # Procesar columna de tiempo si existe
        if 'Time' in df1.columns:
            df1['Time'] = pd.to_datetime(df1['Time'])
            df1 = df1.set_index('Time')

        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Monitoreo en Tiempo Real", "📊 Análisis de Seguridad", "🔍 Filtros y Alertas", "🏠 Información del Restaurante"])

        with tab1:
            st.subheader('Monitoreo de Niveles de Gas Propano')
            
            # Safety indicators
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_value = df1["variable"].iloc[-1]
                if current_value > 80:
                    st.error(f"🚨 Nivel Actual: {current_value:.1f}% - ALERTA")
                elif current_value > 60:
                    st.warning(f"⚠️ Nivel Actual: {current_value:.1f}% - ADVERTENCIA")
                else:
                    st.success(f"✅ Nivel Actual: {current_value:.1f}% - NORMAL")
            
            with col2:
                avg_value = df1["variable"].mean()
                st.metric("Nivel Promedio", f"{avg_value:.1f}%")
            
            with col3:
                max_value = df1["variable"].max()
                st.metric("Nivel Máximo Registrado", f"{max_value:.1f}%")
            
            # Chart type selector
            chart_type = st.selectbox(
                "Tipo de visualización",
                ["Línea", "Área", "Barra"]
            )
            
            # Create plot based on selection
            if chart_type == "Línea":
                st.line_chart(df1["variable"])
            elif chart_type == "Área":
                st.area_chart(df1["variable"])
            else:
                st.bar_chart(df1["variable"])

            # Raw data display with toggle
            if st.checkbox('Mostrar datos crudos del sensor'):
                st.write(df1)

        with tab2:
            st.subheader('Análisis de Seguridad y Estadísticas')
            
            # Statistical summary
            stats_df = df1["variable"].describe()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("#### Resumen Estadístico")
                st.dataframe(stats_df)
            
            with col2:
                st.write("#### Indicadores de Seguridad")
                
                # Safety metrics
                safety_threshold = 80
                warning_threshold = 60
                
                high_readings = len(df1[df1["variable"] > safety_threshold])
                warning_readings = len(df1[df1["variable"] > warning_threshold])
                total_readings = len(df1)
                
                st.metric("Lecturas en Nivel Peligroso", f"{high_readings}", 
                         delta=f"{(high_readings/total_readings*100):.1f}% del total")
                st.metric("Lecturas en Nivel de Advertencia", f"{warning_readings}",
                         delta=f"{(warning_readings/total_readings*100):.1f}% del total")
                st.metric("Tiempo de Operación Segura", 
                         f"{(total_readings - high_readings)/total_readings*100:.1f}%")

        with tab3:
            st.subheader('Filtros y Sistema de Alertas')
            
            # Calcular rango de valores
            min_value = float(df1["variable"].min())
            max_value = float(df1["variable"].max())
            mean_value = float(df1["variable"].mean())
            
            # Sistema de alertas
            st.write("### 🚨 Configuración de Alertas")
            alert_threshold = st.slider(
                'Umbral de alerta de gas (%)',
                min_value=min_value,
                max_value=max_value,
                value=75.0,
                step=1.0
            )
            
            alert_count = len(df1[df1["variable"] > alert_threshold])
            st.info(f"**Alertas activas:** {alert_count} lecturas superan el {alert_threshold}%")
            
            if min_value == max_value:
                st.warning(f"⚠️ Todos los valores en el dataset son iguales: {min_value:.2f}%")
                st.info("No es posible aplicar filtros cuando no hay variación en los datos.")
                st.dataframe(df1)
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Minimum value filter
                    min_val = st.slider(
                        'Filtrar por nivel mínimo de gas (%)',
                        min_value,
                        max_value,
                        mean_value,
                        key="min_val"
                    )
                    
                    filtrado_df_min = df1[df1["variable"] > min_val]
                    st.write(f"Registros con nivel superior al {min_val:.1f}%:")
                    st.dataframe(filtrado_df_min)
                    
                with col2:
                    # Maximum value filter
                    max_val = st.slider(
                        'Filtrar por nivel máximo de gas (%)',
                        min_value,
                        max_value,
                        mean_value,
                        key="max_val"
                    )
                    
                    filtrado_df_max = df1[df1["variable"] < max_val]
                    st.write(f"Registros con nivel inferior al {max_val:.1f}%:")
                    st.dataframe(filtrado_df_max)

                # Download filtered data
                if st.button('Descargar reporte de gas'):
                    csv = filtrado_df_min.to_csv().encode('utf-8')
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name='reporte_gas_restaurante.csv',
                        mime='text/csv',
                    )

        with tab4:
            st.subheader("Información del Restaurante")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### 📍 Información de Contacto")
                st.write("**Restaurante La Cazuela Antioqueña**")
                st.write("- 📞 Teléfono: +57 (4) 444-1234")
                st.write("- 📧 Email: seguridad@cazuelaantioquena.com")
                st.write("- 🏠 Dirección: Carrera 37 #8-45, El Poblado")
                st.write("- 🕒 Horario: 7:00 AM - 11:00 PM")
                
                st.write("### 🔧 Personal de Seguridad")
                st.write("- Jefe de Cocina: Carlos Rodríguez")
                st.write("- Técnico de Gas: María González")
                st.write("- Supervisor: Andrés López")
            
            with col2:
                st.write("### 🔥 Especificaciones del Sistema de Gas")
                st.write("- **Tipo de Gas:** Propano")
                st.write("- **Capacidad Tanque:** 100 kg")
                st.write("- **Sensor:** MQ-6 (Detección de GLP)")
                st.write("- **Rango de Medición:** 0-100% concentración")
                st.write("- **Umbral Crítico:** 80%")
                st.write("- **Umbral Advertencia:** 60%")
                st.write("- **Frecuencia de Monitoreo:** Cada 5 minutos")
                
                st.write("### 📋 Protocolos de Emergencia")
                st.write("1. Nivel >80%: Cierre automático de válvulas")
                st.write("2. Nivel >70%: Notificación inmediata al supervisor")
                st.write("3. Nivel >60%: Verificación manual del sistema")

    except Exception as e:
        st.error(f'Error al procesar el archivo: {str(e)}')
        st.info('Asegúrese de que el archivo CSV tenga el formato correcto con datos del sensor de gas.')
else:
    st.info('''
    💡 **Instrucciones:** 
    - Cargue un archivo CSV con los datos del sensor de gas
    - El archivo debe contener columnas de tiempo y niveles de gas
    - Los datos se analizarán automáticamente para detectar anomalías
    ''')
    
# Footer
st.markdown("""
    ---
    **Sistema desarrollado para Restaurante La Cazuela Antioqueña** 🍲  
    *Cocina Tradicional Paisa · Medellín, Colombia · 2024*  
    *Monitoreo de seguridad para garantizar la calidad de nuestro servicio*
""")
