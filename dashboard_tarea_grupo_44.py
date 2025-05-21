# --- CÓDIGO PARA dashboard_tarea_grupo_X.py ---
# (Este bloque NO se ejecuta directamente en Jupyter)

# dashboard_tarea.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página del dashboard
st.set_page_config(layout="wide", page_title="Dashboard de Ventas de Supermercado")

# --- Carga y Cacheo de Datos ---
# Usamos st.cache_data para mejorar el rendimiento, evitando recargar los datos en cada interacción.
@st.cache_data
def load_data():
    """
    Carga los datos desde un archivo CSV, convierte la columna 'Date' a datetime
    y se asegura que 'gross income' sea numérico.
    """
    data = pd.read_csv('data.csv')
    data['Date'] = pd.to_datetime(data['Date'])
    # Asegurarse que 'gross income' es numérico. 'coerce' convertirá errores a NaT.
    data['gross income'] = pd.to_numeric(data['gross income'], errors='coerce')
    # Eliminar filas donde 'gross income' no pudo ser convertido y es NaN, si alguna.
    data.dropna(subset=['gross income'], inplace=True)
    # Asegurarse que 'cogs' (cost of goods sold) también sea numérico
    data['cogs'] = pd.to_numeric(data['cogs'], errors='coerce')
    data.dropna(subset=['cogs'], inplace=True)
    return data

df = load_data()

# --- Barra Lateral de Filtros ---
st.sidebar.header("Filtros del Dashboard")

# Filtro de Sucursal: Permite seleccionar una o todas las sucursales.
branches = ['Todas'] + sorted(df['Branch'].unique().tolist())
selected_branch = st.sidebar.selectbox('Seleccionar Sucursal:', branches)

# Filtro de Línea de Producto: Permite seleccionar una o todas las líneas de producto.
product_lines = ['Todas'] + sorted(df['Product line'].unique().tolist())
selected_product_line = st.sidebar.selectbox('Seleccionar Línea de Producto:', product_lines)

# Filtro de Tipo de Cliente: Permite seleccionar un tipo de cliente o todos.
customer_types = ['Todos'] + sorted(df['Customer type'].unique().tolist())
selected_customer_type = st.sidebar.selectbox('Seleccionar Tipo de Cliente:', customer_types)

# Filtro de Rango de Fechas: Permite seleccionar un intervalo de fechas.
min_date = df['Date'].min()
max_date = df['Date'].max()
selected_date_range = st.sidebar.date_input(
    "Seleccionar Rango de Fechas:",
    value=(min_date, max_date), # Valor por defecto es el rango completo
    min_value=min_date,
    max_value=max_date
)

# --- Aplicación de Filtros al DataFrame ---
# Se crea una copia del DataFrame original para no modificarlo.
filtered_df = df.copy()

# Aplicar filtro de sucursal si no se seleccionó 'Todas'.
if selected_branch != 'Todas':
    filtered_df = filtered_df[filtered_df['Branch'] == selected_branch]

# Aplicar filtro de línea de producto si no se seleccionó 'Todas'.
if selected_product_line != 'Todas':
    filtered_df = filtered_df[filtered_df['Product line'] == selected_product_line]

# Aplicar filtro de tipo de cliente si no se seleccionó 'Todos'.
if selected_customer_type != 'Todos':
    filtered_df = filtered_df[filtered_df['Customer type'] == selected_customer_type]

# Aplicar filtro de rango de fechas.
if len(selected_date_range) == 2: # Asegura que se seleccionaron fecha de inicio y fin.
    filtered_df = filtered_df[
        (filtered_df['Date'] >= pd.to_datetime(selected_date_range[0])) &
        (filtered_df['Date'] <= pd.to_datetime(selected_date_range[1]))
    ]


# --- Título Principal del Dashboard ---
st.title("📊 Dashboard Analítico de Ventas de Supermercado")
st.markdown("Este dashboard presenta un análisis interactivo de los datos de ventas de una cadena de tiendas de conveniencia. Utiliza los filtros en la barra lateral para explorar los datos.")
st.markdown("---")

# --- Métricas Clave (KPIs) ---
st.header("Métricas Clave (KPIs)")
# Solo mostrar KPIs si hay datos después de filtrar.
if not filtered_df.empty:
    total_revenue = filtered_df['Total'].sum()
    total_gross_income = filtered_df['gross income'].sum()
    average_rating = filtered_df['Rating'].mean()
    num_transactions = filtered_df['Invoice ID'].nunique()

    # Organizar KPIs en columnas para una mejor presentación.
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos Totales", f"${total_revenue:,.2f}")
    col2.metric("Ingreso Bruto Total", f"${total_gross_income:,.2f}")
    col3.metric("Calificación Promedio", f"{average_rating:.2f} ⭐")
    col4.metric("Número de Transacciones", f"{num_transactions:,}")
else:
    st.warning("No hay datos disponibles para los filtros seleccionados. Por favor, ajusta los filtros.")

st.markdown("---")


# --- Visualizaciones Detalladas ---
st.header("Visualizaciones Detalladas")

# Organizar los primeros cuatro gráficos en dos columnas.
col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    st.subheader("1. Evolución de las Ventas Totales")
    if not filtered_df.empty:
        # Agrupar por día para la evolución de ventas.
        sales_over_time_filtered = filtered_df.groupby(filtered_df['Date'].dt.to_period("D"))['Total'].sum().reset_index()
        # Convertir Period a Timestamp para que Plotly lo maneje correctamente.
        sales_over_time_filtered['Date'] = sales_over_time_filtered['Date'].dt.to_timestamp()
        fig_sales_evolution = px.line(sales_over_time_filtered, x='Date', y='Total',
                                      labels={'Date': 'Fecha', 'Total': 'Ventas Totales ($)'}, height=400)
        fig_sales_evolution.update_layout(margin=dict(l=20, r=20, t=30, b=20)) # Ajustar márgenes
        st.plotly_chart(fig_sales_evolution, use_container_width=True)
    else:
        st.info("No hay datos para mostrar la evolución de ventas con los filtros actuales.")

    st.subheader("3. Distribución de Calificaciones de Clientes")
    if not filtered_df.empty:
        fig_rating_distribution = px.histogram(filtered_df, x='Rating', nbins=10, # nbins puede ajustarse
                                             labels={'Rating': 'Calificación (Rating)', 'count': 'Frecuencia'},
                                             marginal="box", # Añade un box plot en el margen
                                             height=400)
        fig_rating_distribution.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_rating_distribution, use_container_width=True)
    else:
        st.info("No hay datos para mostrar la distribución de calificaciones con los filtros actuales.")

with col_viz2:
    st.subheader("2. Ingresos por Línea de Producto")
    if not filtered_df.empty:
        revenue_by_product_line_filtered = filtered_df.groupby('Product line')['Total'].sum().reset_index().sort_values(by='Total', ascending=False)
        fig_revenue_product = px.bar(revenue_by_product_line_filtered, x='Product line', y='Total',
                                     labels={'Product line': 'Línea de Producto', 'Total': 'Ingresos Totales ($)'},
                                     color='Product line', # Colorear barras por línea de producto
                                     height=400)
        fig_revenue_product.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_revenue_product, use_container_width=True)
    else:
        st.info("No hay datos para mostrar ingresos por línea de producto con los filtros actuales.")


    st.subheader("4. Gasto Total por Tipo de Cliente")
    if not filtered_df.empty:
        fig_spending_customer_type = px.box(filtered_df, x='Customer type', y='Total',
                                            labels={'Customer type': 'Tipo de Cliente', 'Total': 'Gasto Total ($)'},
                                            color='Customer type', # Colorear por tipo de cliente
                                            height=400)
        fig_spending_customer_type.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_spending_customer_type, use_container_width=True)
    else:
        st.info("No hay datos para mostrar el gasto por tipo de cliente con los filtros actuales.")


# --- Gráficos Adicionales ---
st.markdown("---")

col_viz_full1, col_viz_full2 = st.columns(2) # Dos columnas para los siguientes dos gráficos

with col_viz_full1:
    st.subheader("5. Métodos de Pago Preferidos")
    if not filtered_df.empty:
        payment_counts_filtered = filtered_df['Payment'].value_counts().reset_index()
        payment_counts_filtered.columns = ['Payment', 'Count'] # Renombrar columnas para Plotly
        fig_payment_methods = px.pie(payment_counts_filtered, names='Payment', values='Count',
                                     hole=0.3, # Efecto donut
                                     height=400)
        fig_payment_methods.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_payment_methods, use_container_width=True)
    else:
        st.info("No hay datos para mostrar métodos de pago con los filtros actuales.")

with col_viz_full2:
    st.subheader("6. Composición del Ingreso Bruto")
    # Este gráfico se adapta si se selecciona una sucursal específica o todas.
    if not filtered_df.empty:
        if selected_branch != 'Todas': # Si se selecciona una sucursal específica
            income_by_product_filtered_single_branch = filtered_df.groupby('Product line')['gross income'].sum().reset_index().sort_values(by='gross income', ascending=False)
            fig_income_composition = px.bar(income_by_product_filtered_single_branch, x='Product line', y='gross income',
                                            color='Product line',
                                            title=f"Ingreso Bruto por Línea de Producto (Sucursal {selected_branch})",
                                            labels={'Product line': 'Línea de Producto', 'gross income': 'Ingreso Bruto ($)'}, height=400)
        else: # Si se seleccionan 'Todas' las sucursales, mostrar comparación entre ellas
            income_by_branch_product_filtered = filtered_df.groupby(['Branch', 'Product line'])['gross income'].sum().reset_index()
            fig_income_composition = px.bar(income_by_branch_product_filtered, x='Branch', y='gross income',
                                            color='Product line', barmode='stack', # Barras apiladas
                                            title="Ingreso Bruto por Sucursal y Línea de Producto",
                                            labels={'Branch': 'Sucursal', 'gross income': 'Ingreso Bruto Total ($)', 'Product line': 'Línea de Producto'},
                                            height=400)
        fig_income_composition.update_layout(margin=dict(l=20, r=20, t=50, b=20)) # Aumentar margen superior para el título
        st.plotly_chart(fig_income_composition, use_container_width=True)
    else:
        st.info("No hay datos para mostrar la composición de ingreso bruto con los filtros actuales.")

st.markdown("---") # Separador antes del nuevo gráfico

# --- NUEVO GRÁFICO: Relación entre Costo y Ganancia Bruta ---
st.subheader("7. Relación entre Costo (COGS) y Ganancia Bruta")
if not filtered_df.empty and 'cogs' in filtered_df.columns and 'gross income' in filtered_df.columns:
    fig_cogs_income_relation = px.scatter(filtered_df, x='cogs', y='gross income',
                                          labels={'cogs': 'Costo de Bienes Vendidos (COGS) ($)', 'gross income': 'Ingreso Bruto ($)'},
                                          title="Relación COGS vs. Ingreso Bruto",
                                          hover_data=['Product line', 'Total', 'Branch'], # Añade más detalles al pasar el mouse
                                          height=500,
                                          trendline="ols", # Añade una línea de tendencia (opcional)
                                          color='Product line' # Colorear por línea de producto (opcional)
                                          )
    fig_cogs_income_relation.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_cogs_income_relation, use_container_width=True)
elif not filtered_df.empty:
    st.warning("Las columnas 'cogs' o 'gross income' no están disponibles o no son numéricas en los datos filtrados para este gráfico.")
else:
    st.info("No hay datos para mostrar la relación COGS vs. Ingreso Bruto con los filtros actuales.")


st.markdown("---")
st.subheader("8. Análisis de Correlación Numérica (Datos Filtrados)") # Renumerado
if not filtered_df.empty:
    # Seleccionar solo columnas numéricas relevantes para la correlación.
    numeric_cols_corr = ['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs', 'gross income', 'Rating']
    # Asegurar que solo columnas existentes y numéricas se usen
    valid_numeric_cols = [col for col in numeric_cols_corr if col in filtered_df.columns and pd.api.types.is_numeric_dtype(filtered_df[col])]

    if len(valid_numeric_cols) > 1: # Se necesita al menos dos columnas para una matriz de correlación
        correlation_matrix_filtered = filtered_df[valid_numeric_cols].corr()
        fig_correlation_heatmap = px.imshow(correlation_matrix_filtered, text_auto=True, aspect="auto",
                                           color_continuous_scale='RdBu_r', # Escala de color divergente (Rojo-Azul)
                                           zmin=-1, zmax=1, # Rango de valores de correlación
                                           height=500)
        fig_correlation_heatmap.update_layout(title_text='Mapa de Calor de Correlación', title_x=0.5, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_correlation_heatmap, use_container_width=True)
    else:
        st.warning("No hay suficientes columnas numéricas válidas en los datos filtrados para mostrar el mapa de correlación.")
else:
    st.info("No hay datos para mostrar el mapa de correlación con los filtros actuales.")


# --- Reflexión sobre Interactividad (Texto en la Barra Lateral) ---
st.sidebar.markdown("---")
st.sidebar.header("Acerca de este Dashboard")
st.sidebar.info(
    "Este dashboard fue creado para el análisis interactivo de las ventas de supermercado. "
    "Utiliza los filtros en la parte superior de esta barra lateral para explorar los datos "
    "desde diferentes perspectivas (sucursal, línea de producto, tipo de cliente y fecha)."
    "\n\n"
    "La interactividad permite a los usuarios finales (como gerentes o analistas de marketing) "
    "profundizar en subconjuntos específicos de datos, facilitando la identificación de patrones, "
    "tendencias y anomalías que podrían no ser evidentes en informes estáticos. "
    "Esto empodera la toma de decisiones basada en datos al permitir una exploración más ágil y personalizada."
)