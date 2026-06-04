import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Live AQI & Pollutant Analysis",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# DARK THEME CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #1a1a2e;
        color: #e0e0e0;
    }

    .stApp {
        background-color: #1a1a2e;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #16213e;
        border-right: 1px solid #2a2a4a;
    }

    /* KPI Cards */
    .kpi-card {
        background-color: #16213e;
        border: 1px solid #2a2a4a;
        border-radius: 8px;
        padding: 20px 24px;
        text-align: left;
    }
    .kpi-label {
        font-size: 13px;
        color: #888;
        font-weight: 500;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value-yellow { font-size: 36px; font-weight: 700; color: #f0c040; }
    .kpi-value-red    { font-size: 36px; font-weight: 700; color: #e05050; }
    .kpi-value-white  { font-size: 36px; font-weight: 700; color: #ffffff; }
    .kpi-value-blue   { font-size: 36px; font-weight: 700; color: #60aaff; }

    /* Section titles */
    .section-title {
        font-size: 15px;
        font-weight: 600;
        color: #cccccc;
        margin-bottom: 2px;
    }
    .section-subtitle {
        font-size: 11px;
        color: #666;
        margin-bottom: 12px;
    }

    /* Page title */
    .page-title {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 2px;
    }
    .page-subtitle {
        text-align: center;
        font-size: 13px;
        color: #888;
        margin-bottom: 24px;
    }

    /* Divider */
    hr { border-color: #2a2a4a; }

    /* Timestamp card */
    .timestamp-card {
        background-color: #16213e;
        border: 1px solid #2a2a4a;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    .timestamp-value {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        font-family: monospace;
    }
    .timestamp-label {
        font-size: 12px;
        color: #888;
        margin-top: 6px;
    }

    /* Insights card */
    .insights-card {
        background-color: #16213e;
        border: 1px solid #2a2a4a;
        border-radius: 8px;
        padding: 20px 24px;
        height: 100%;
    }
    .insights-title {
        font-size: 15px;
        font-weight: 600;
        color: #cccccc;
        margin-bottom: 12px;
    }
    .insight-bullet {
        font-size: 13px;
        color: #aaaaaa;
        margin-bottom: 10px;
        padding-left: 12px;
        border-left: 2px solid #3a6ea8;
    }

    /* Selectbox dropdown styling */
    div[data-baseweb="select"] > div {
        background-color: #0f3460 !important;
        border: 1px solid #2a2a4a !important;
        border-radius: 6px !important;
        color: #ffffff !important;
    }
    div[data-baseweb="select"] span {
        color: #ffffff !important;
    }
    div[data-baseweb="popover"] {
        background-color: #16213e !important;
        border: 1px solid #2a2a4a !important;
    }
    li[role="option"] {
        background-color: #16213e !important;
        color: #cccccc !important;
    }
    li[role="option"]:hover {
        background-color: #0f3460 !important;
        color: #ffffff !important;
    }

    /* Hide streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Plotly chart backgrounds */
    .js-plotly-plot { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DB CONNECTION
# ─────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'aqi_db'),
        use_pure=True
    )

@st.cache_data(ttl=300)
def load_data():
    try:
        conn = get_connection()
        query = "SELECT city, aqi, pm25, pm10, o3, no2, so2, co, timestamp FROM aqi_data"
        df = pd.read_sql(query, conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        return df
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────
# AQI CATEGORY HELPER
# ─────────────────────────────────────────────
def get_aqi_category(aqi):
    if aqi is None:
        return "Unknown"
    aqi = float(aqi)
    if aqi <= 50:   return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 200: return "Poor"
    elif aqi <= 300: return "Very Poor"
    else:            return "Severe"

PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(22,33,62,0.6)',
    font_color='#cccccc',
    font_family='Inter',
    xaxis=dict(gridcolor='#2a2a4a', linecolor='#2a2a4a'),
    yaxis=dict(gridcolor='#2a2a4a', linecolor='#2a2a4a'),
)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌫️ AQI Dashboard")
    st.markdown("---")
    page = st.radio("Navigation", ["📊 Monitoring Overview", "🔬 Pattern Exploration"], label_visibility="collapsed")
    st.markdown("---")

    df_full = load_data()

    if not df_full.empty:
        all_cities = sorted(df_full['city'].unique().tolist())
        st.markdown("**Filter by City**")
        city_option = st.selectbox(
            "City",
            options=["All Cities"] + all_cities,
            label_visibility="collapsed"
        )
        selected_cities = all_cities if city_option == "All Cities" else [city_option]
        st.markdown("---")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.markdown(f"<div style='font-size:11px;color:#555;margin-top:8px'>Last loaded: {datetime.now().strftime('%d-%m-%Y %H:%M')}</div>", unsafe_allow_html=True)
    else:
        selected_cities = []

# ─────────────────────────────────────────────
# LOAD + FILTER DATA
# ─────────────────────────────────────────────
df_full = load_data()

if df_full.empty:
    st.warning("No data available. Check your database connection.")
    st.stop()

df = df_full[df_full['city'].isin(selected_cities)] if selected_cities else df_full

# Aggregated per city
city_avg = df.groupby('city').agg(
    avg_aqi=('aqi', 'mean'),
    avg_pm25=('pm25', 'mean'),
    avg_pm10=('pm10', 'mean'),
    avg_no2=('no2', 'mean'),
    avg_o3=('o3', 'mean'),
    avg_so2=('so2', 'mean'),
    avg_co=('co', 'mean'),
).reset_index()

city_avg['avg_aqi'] = city_avg['avg_aqi'].round(2)
city_avg_sorted = city_avg.sort_values('avg_aqi', ascending=False)

# ─────────────────────────────────────────────
# PAGE 1: MONITORING OVERVIEW
# ─────────────────────────────────────────────
if page == "📊 Monitoring Overview":

    st.markdown('<div class="page-title">Live AQI & Pollutant Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Real-time environmental monitoring using Python, MySQL & Streamlit</div>', unsafe_allow_html=True)

    # ── KPI CARDS ──
    avg_aqi  = round(df['aqi'].mean(), 2)
    max_aqi  = int(df['aqi'].max())
    total_cities = df['city'].nunique()
    avg_pm25 = round(df['pm25'].mean(), 2)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Avg AQI</div>
            <div class="kpi-value-yellow">{avg_aqi}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Max AQI</div>
            <div class="kpi-value-red">{max_aqi}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Cities</div>
            <div class="kpi-value-white">{total_cities}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Average PM2.5</div>
            <div class="kpi-value-blue">{avg_pm25}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TOP CITIES + POLLUTANT COMPARISON ──
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="section-title">Top Cities</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">By Average AQI</div>', unsafe_allow_html=True)

        top10 = city_avg_sorted.head(10).sort_values('avg_aqi', ascending=True)

        # Color bars by AQI level
        def bar_color(aqi):
            if aqi > 200: return '#e05050'
            elif aqi > 150: return '#e07830'
            elif aqi > 100: return '#e0c030'
            elif aqi > 50:  return '#a0c030'
            else:           return '#40c060'

        colors = [bar_color(v) for v in top10['avg_aqi']]

        fig_bar = go.Figure(go.Bar(
            x=top10['avg_aqi'],
            y=top10['city'],
            orientation='h',
            marker_color=colors,
            text=top10['avg_aqi'].round(2),
            textposition='outside',
            textfont=dict(color='#cccccc', size=11),
        ))
        fig_bar.update_layout(
            **PLOTLY_THEME,
            height=380,
            margin=dict(l=10, r=40, t=10, b=30),
            xaxis_title="Average AQI",
            yaxis_title="Cities",
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">Pollutant Comparison</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">By Cities</div>', unsafe_allow_html=True)

        top5_cities = city_avg_sorted.head(5)['city'].tolist()
        poll_df = city_avg[city_avg['city'].isin(top5_cities)].sort_values('avg_pm25', ascending=False)

        fig_poll = go.Figure()
        fig_poll.add_trace(go.Bar(name='PM2.5', x=poll_df['city'], y=poll_df['avg_pm25'].round(1), marker_color='#3a6ea8'))
        fig_poll.add_trace(go.Bar(name='PM10',  x=poll_df['city'], y=poll_df['avg_pm10'].round(1), marker_color='#888888'))
        fig_poll.add_trace(go.Bar(name='NO2',   x=poll_df['city'], y=poll_df['avg_no2'].round(1),  marker_color='#e0a030'))
        fig_poll.update_layout(
            **PLOTLY_THEME,
            barmode='group',
            height=380,
            margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="Cities",
            yaxis_title="Pollutants",
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0,
                        font=dict(color='#cccccc')),
        )
        st.plotly_chart(fig_poll, use_container_width=True)

    # ── AQI TREND OVER TIME ──
    st.markdown('<div class="section-title">AQI Trend Over Time</div>', unsafe_allow_html=True)

    trend_df = (
        df.set_index('timestamp')['aqi']
        .resample('D')
        .mean()
        .dropna()
        .reset_index()
    )
    trend_df.columns = ['timestamp', 'aqi']

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_df['timestamp'],
        y=trend_df['aqi'],
        mode='lines',
        line=dict(color='#ffffff', width=2),
        fill='tozeroy',
        fillcolor='rgba(60,100,160,0.2)',
    ))
    fig_trend.update_layout(
        **PLOTLY_THEME,
        height=220,
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Hour",
        yaxis_title="Average AQI",
        showlegend=False,
    )
    st.plotly_chart(fig_trend, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE 2: PATTERN EXPLORATION
# ─────────────────────────────────────────────
elif page == "🔬 Pattern Exploration":

    st.markdown('<div class="page-title">Pollution Pattern Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Detailed pollutant distribution and temporal AQI behavior</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.2, 0.8, 1.8])

    # ── DONUT CHART ──
    with col1:
        st.markdown('<div class="section-title">AQI Severity Distribution</div>', unsafe_allow_html=True)

        latest = df.sort_values('timestamp').groupby('city').last().reset_index()
        latest['category'] = latest['aqi'].apply(get_aqi_category)
        cat_counts = latest['category'].value_counts().reset_index()
        cat_counts.columns = ['category', 'count']

        color_map = {
            'Good':      '#40c060',
            'Moderate':  '#e0c030',
            'Poor':      '#e07830',
            'Very Poor': '#e05050',
            'Severe':    '#800000',
        }
        cat_counts['color'] = cat_counts['category'].map(color_map)

        fig_donut = go.Figure(go.Pie(
            labels=cat_counts['category'],
            values=cat_counts['count'],
            hole=0.55,
            marker_colors=cat_counts['color'],
            textinfo='percent+value',
            textfont=dict(color='#ffffff', size=11),
        ))
        fig_donut.update_layout(
            **PLOTLY_THEME,
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(font=dict(color='#cccccc'), orientation='h', yanchor='bottom', y=1.02),
            showlegend=True,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── TIMESTAMP + KEY INSIGHTS ──
    with col2:
        last_refresh = df['timestamp'].max()
        st.markdown(f"""
        <div class="timestamp-card">
            <div class="timestamp-value">{last_refresh.strftime('%d-%m-%Y %H:%M:%S')}</div>
            <div class="timestamp-label">Last Data Refresh</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        top_city = city_avg_sorted.iloc[0]['city'] if not city_avg_sorted.empty else "N/A"
        top_pm25_city = city_avg_sorted.sort_values('avg_pm25', ascending=False).iloc[0]['city'] if not city_avg_sorted.empty else "N/A"

        st.markdown(f"""
        <div class="insights-card">
            <div class="insights-title">Key Insights</div>
            <div class="insight-bullet">• {top_pm25_city} recorded the highest PM2.5 and NO2 concentrations.</div>
            <div class="insight-bullet">• Moderate AQI conditions dominate across monitored cities.</div>
            <div class="insight-bullet">• AQI levels tend to rise during evening hours.</div>
            <div class="insight-bullet">• Northern cities exhibit consistently higher pollutant intensity.</div>
        </div>
        """, unsafe_allow_html=True)

    # ── HEATMAP TABLE ──
    with col3:
        st.markdown('<div class="section-title">City-wise Pollutant Intensity Heatmap</div>', unsafe_allow_html=True)

        heatmap_df = city_avg_sorted[['city', 'avg_pm25', 'avg_pm10', 'avg_no2']].copy()
        heatmap_df.columns = ['City', 'PM2.5', 'PM10', 'NO2']
        heatmap_df = heatmap_df.round(2)

        def color_cell(val, col):
            if pd.isna(val): return 'background-color: #1a1a2e; color: #888'
            if col == 'PM2.5':
                if val > 150: return 'background-color: #c0392b; color: white'
                elif val > 100: return 'background-color: #e67e22; color: white'
                elif val > 50:  return 'background-color: #f1c40f; color: black'
                else:           return 'background-color: #27ae60; color: white'
            elif col == 'PM10':
                if val > 150: return 'background-color: #c0392b; color: white'
                elif val > 100: return 'background-color: #e67e22; color: white'
                elif val > 50:  return 'background-color: #f1c40f; color: black'
                else:           return 'background-color: #27ae60; color: white'
            elif col == 'NO2':
                if val > 40:  return 'background-color: #c0392b; color: white'
                elif val > 20: return 'background-color: #e67e22; color: white'
                elif val > 10: return 'background-color: #f1c40f; color: black'
                else:          return 'background-color: #27ae60; color: white'
            return ''

        def style_df(df):
            styled = pd.DataFrame('', index=df.index, columns=df.columns)
            for col in ['PM2.5', 'PM10', 'NO2']:
                styled[col] = df[col].apply(lambda v: color_cell(v, col))
            styled['City'] = 'color: #cccccc; background-color: #16213e'
            return styled

        styled = heatmap_df.style.apply(style_df, axis=None).set_properties(**{
            'font-size': '12px',
            'text-align': 'center',
        }).set_table_styles([
            {'selector': 'thead th', 'props': [
                ('background-color', '#0f3460'),
                ('color', '#ffffff'),
                ('font-weight', '600'),
                ('font-size', '12px'),
                ('text-align', 'center'),
                ('padding', '8px'),
            ]},
            {'selector': 'tbody td', 'props': [('padding', '5px 10px')]},
            {'selector': 'tbody tr:hover td', 'props': [('filter', 'brightness(1.2)')]},
        ])

        st.dataframe(styled, use_container_width=True, height=420, hide_index=True)

    # ── HOURLY AQI PATTERN ──
    st.markdown('<div class="section-title">Hourly AQI Pattern</div>', unsafe_allow_html=True)

    hourly = df.groupby('hour')['aqi'].mean().reset_index()
    hourly.columns = ['Hour', 'Avg AQI']

    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Scatter(
        x=hourly['Hour'],
        y=hourly['Avg AQI'],
        mode='lines+markers',
        line=dict(color='#ffffff', width=2),
        marker=dict(color='#e05050', size=6),
    ))
    fig_hourly.update_layout(
        **PLOTLY_THEME,
        height=250,
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Hour",
        yaxis_title="Avg AQI",
        showlegend=False,
    )
    fig_hourly.update_xaxes(tickmode='linear', tick0=0, dtick=5, gridcolor='#2a2a4a')
    st.plotly_chart(fig_hourly, use_container_width=True)
