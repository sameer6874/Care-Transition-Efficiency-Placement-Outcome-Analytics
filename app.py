import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="UAC Pipeline Analytics",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Data Processing Pipeline
# ---------------------------------------------------------
@st.cache_data
def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=['Date'])
    
    cols = {
        'date': 'Date',
        'apprehended': 'Children apprehended and placed in CBP custody*',
        'cbp_custody': 'Children in CBP custody',
        'transferred': 'Children transferred out of CBP custody',
        'hhs_care': 'Children in HHS Care',
        'discharged': 'Children discharged from HHS Care'
    }
    
    # Clean and type conversion
    for key, col in cols.items():
        if key != 'date':
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '').replace('nan', '0').astype(float)
            else:
                df[col] = df[col].fillna(0)
                
    df[cols['date']] = pd.to_datetime(df[cols['date']], errors='coerce')
    df = df.dropna(subset=[cols['date']]).sort_values(cols['date'])
    
    # Feature Engineering (KPIs)
    df['Transfer Efficiency'] = np.where(df[cols['cbp_custody']] > 0, df[cols['transferred']] / df[cols['cbp_custody']], 0)
    df['Discharge Effectiveness'] = np.where(df[cols['hhs_care']] > 0, df[cols['discharged']] / df[cols['hhs_care']], 0)
    df['Pipeline Throughput'] = np.where(df[cols['apprehended']] > 0, df[cols['discharged']] / df[cols['apprehended']], 0)
    df['Backlog Volume'] = df[cols['apprehended']] - df[cols['discharged']]
    df['Outcome Stability (7d Std)'] = df['Discharge Effectiveness'].rolling(window=7, min_periods=1).std().fillna(0)
    
    return df, cols

try:
    file_path = "HHS_Unaccompanied_Alien_Children_Program.csv"
    data, cols = load_and_clean_data(file_path)
except Exception as e:
    st.error(f"System Error: Unable to interface with dataset. {e}")
    st.stop()

# ---------------------------------------------------------
# Sidebar & Theme Selection
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Analytical Parameters")
    
    min_d, max_d = data['Date'].min().date(), data['Date'].max().date()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", min_d, min_value=min_d, max_value=max_d, format="MM/DD/YYYY")
    with col2:
        end_date = st.date_input("To Date", max_d, min_value=min_d, max_value=max_d, format="MM/DD/YYYY")
        
    if start_date > end_date:
        st.error("❌ 'From Date' must be before or equal to 'To Date'.")
        st.stop()
        
    st.markdown("---")
    
    # Theme Selection
    themes = {
        "Clean White": {"bg": "#ffffff", "text": "#31333F", "card": "rgba(241, 245, 249, 0.8)", "title": "#475569", "plotly": "plotly_white", "font": "#475569"},
        "Soft Pearl": {"bg": "#F9F9F6", "text": "#4A4A4A", "card": "rgba(240, 235, 225, 0.8)", "title": "#6B6B6B", "plotly": "plotly_white", "font": "#4A4A4A"},
        "Mint Breeze": {"bg": "#F2FBF7", "text": "#2C4C3B", "card": "rgba(215, 240, 225, 0.8)", "title": "#3C6E53", "plotly": "plotly_white", "font": "#2C4C3B"},
        "Ice Blue": {"bg": "#F0F8FF", "text": "#1A365D", "card": "rgba(226, 241, 255, 0.8)", "title": "#2B6CB0", "plotly": "plotly_white", "font": "#1A365D"},
        "Warm Sand": {"bg": "#FDFBF7", "text": "#594A3F", "card": "rgba(245, 235, 220, 0.8)", "title": "#8A7360", "plotly": "plotly_white", "font": "#594A3F"},
        "Lavender Mist": {"bg": "#F8F5FA", "text": "#4A3B52", "card": "rgba(235, 225, 240, 0.8)", "title": "#6D5477", "plotly": "plotly_white", "font": "#4A3B52"},
        "Rose Gold": {"bg": "#FFF7F5", "text": "#5C3A35", "card": "rgba(255, 228, 225, 0.8)", "title": "#A05A51", "plotly": "plotly_white", "font": "#5C3A35"},
        "Lemon Chiffon": {"bg": "#FFFCF0", "text": "#595333", "card": "rgba(255, 248, 215, 0.8)", "title": "#8C8347", "plotly": "plotly_white", "font": "#595333"},
        "Silver Metallic": {"bg": "#F5F5F5", "text": "#333333", "card": "rgba(224, 224, 224, 0.8)", "title": "#666666", "plotly": "plotly_white", "font": "#333333"},
        "Corporate Slate": {"bg": "#F1F5F9", "text": "#1E293B", "card": "rgba(226, 232, 240, 0.8)", "title": "#334155", "plotly": "plotly_white", "font": "#1E293B"}
    }
    theme_choice = st.selectbox("🎨 Dashboard Theme", list(themes.keys()), index=6)
    
    st.markdown("---")
    st.markdown("### 📑 Navigation")
    st.info("Utilize the tabs in the main window to navigate between live analytics and official policy documentation.")

# ---------------------------------------------------------
# Dynamic CSS & Theme Variables
# ---------------------------------------------------------
theme_dict = themes[theme_choice]
bg_color = theme_dict["bg"]
text_color = theme_dict["text"]
card_bg = theme_dict["card"]
card_title_color = theme_dict["title"]
plotly_template = theme_dict["plotly"]
font_color = theme_dict["font"]

st.markdown(f"""
<style>
    /* Global Typography & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* Force Streamlit Background */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stHeader"] {{
        background-color: {bg_color};
    }}
    
    /* Force Text Colors to override Streamlit Base Theme */
    h1, h2, h3, h4, h5, h6, p, label, li, .stMarkdown, .stText {{
        color: {text_color} !important;
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Main Gradient Header */
    .premium-header {{
        color: {text_color} !important;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }}
    .sub-header {{
        color: {card_title_color};
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }}

    /* Glassmorphism Metric Cards */
    .metric-container {{
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 2rem;
    }}
    .glass-card {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(128, 128, 128, 0.1);
        border-radius: 12px;
        padding: 20px;
        flex: 1;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }}
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
    }}
    .card-title {{
        color: {card_title_color};
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 10px;
    }}
    .card-value {{
        font-size: 2.2rem;
        font-weight: 700;
    }}
    
    /* Specific metric colors */
    .val-blue {{ color: #0284c7; }}
    .val-green {{ color: #10b981; }}
    .val-purple {{ color: #8b5cf6; }}
    .val-red {{ color: #ef4444; }}
    
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# UI Layout & Components
# ---------------------------------------------------------
st.markdown('<h1 class="premium-header">UAC System Operations Portal</h1>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Executive Dashboard for Care Pipeline Process Efficiency & Outcomes Analysis</div>', unsafe_allow_html=True)

filtered = data[(data['Date'].dt.date >= start_date) & (data['Date'].dt.date <= end_date)].copy()

if filtered.empty:
    st.markdown('<div style="color: #ff4b4b; padding: 10px; border: 1px solid #ff4b4b; border-radius: 5px; margin-bottom: 20px;">'
                '❌ <b>No data available</b> for the selected dates.'
                '</div>', unsafe_allow_html=True)
    st.stop()

# Top KPIs
avg_te = filtered['Transfer Efficiency'].mean()
avg_de = filtered['Discharge Effectiveness'].mean()
avg_tp = filtered['Pipeline Throughput'].mean()
net_bl = filtered['Backlog Volume'].sum()
bl_color = "val-red" if net_bl > 0 else "val-green"

st.markdown(f"""
<div class="metric-container">
    <div class="glass-card">
        <div class="card-title">Transfer Efficiency</div>
        <div class="card-value val-blue">{avg_te:.1%}</div>
    </div>
    <div class="glass-card">
        <div class="card-title">Discharge Effectiveness</div>
        <div class="card-value val-green">{avg_de:.1%}</div>
    </div>
    <div class="glass-card">
        <div class="card-title">Pipeline Throughput</div>
        <div class="card-value val-purple">{avg_tp:.1%}</div>
    </div>
    <div class="glass-card">
        <div class="card-title">Net Backlog (Period)</div>
        <div class="card-value {bl_color}">{int(net_bl):,}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs([
    "📊 System Flow & Capacity", 
    "📈 Process Bottlenecks"
])

# Shared Plotly configuration for premium look
plotly_layout = dict(
    template=plotly_template,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    hovermode='x unified',
    font=dict(family="Inter", size=12, color=font_color),
    title_font=dict(color=font_color),
    legend=dict(font=dict(color=font_color)),
    margin=dict(l=20, r=20, t=50, b=20)
)

with tab1:
    st.markdown("### Care Pipeline Capacity vs Flow Dynamics")
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=filtered['Date'], y=filtered[cols['cbp_custody']], mode='lines', 
                              name='Active CBP Custody', line=dict(color='#ef4444', width=2), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.1)'))
    fig1.add_trace(go.Scatter(x=filtered['Date'], y=filtered[cols['hhs_care']], mode='lines', 
                              name='Active HHS Care', line=dict(color='#0ea5e9', width=2), fill='tozeroy', fillcolor='rgba(14, 165, 233, 0.1)'))
    
    fig1.update_layout(**plotly_layout, title="System Inventory Analysis (Active Care Loads)", yaxis_title="Active Cases")
    st.plotly_chart(fig1, use_container_width=True, theme=None)
    
    col1, col2 = st.columns(2)
    with col1:
        fig_te = px.line(filtered, x='Date', y='Transfer Efficiency', color_discrete_sequence=['#8b5cf6'])
        fig_te.add_hline(y=avg_te, line_dash="dash", line_color="rgba(128,128,128,0.5)", annotation_text="Avg")
        fig_te.update_layout(**plotly_layout, title="CBP to HHS Transfer Efficiency Ratio", yaxis_tickformat='.1%')
        st.plotly_chart(fig_te, use_container_width=True, theme=None)
        
    with col2:
        fig_de = px.line(filtered, x='Date', y='Discharge Effectiveness', color_discrete_sequence=['#10b981'])
        fig_de.add_hline(y=avg_de, line_dash="dash", line_color="rgba(128,128,128,0.5)", annotation_text="Avg")
        fig_de.update_layout(**plotly_layout, title="HHS Discharge Effectiveness Index", yaxis_tickformat='.1%')
        st.plotly_chart(fig_de, use_container_width=True, theme=None)

with tab2:
    st.markdown("### Process Congestion & Bottleneck Diagnostics")
    
    fig_bl = go.Figure()
    fig_bl.add_trace(go.Bar(
        x=filtered['Date'], y=filtered['Backlog Volume'], name='Daily Net Backlog',
        marker_color=np.where(filtered['Backlog Volume'] > 0, '#ef4444', '#10b981'),
        opacity=0.8
    ))
    filtered['Backlog (7d)'] = filtered['Backlog Volume'].rolling(7, min_periods=1).mean()
    fig_bl.add_trace(go.Scatter(x=filtered['Date'], y=filtered['Backlog (7d)'], mode='lines',
                                name='7-Day Trend', line=dict(color='#94a3b8', width=3)))
    
    fig_bl.update_layout(**plotly_layout, title="Pipeline Bottleneck (Daily Intake vs Outflow)", yaxis_title="Net Case Accumulation")
    st.plotly_chart(fig_bl, use_container_width=True, theme=None)
    
    st.markdown("#### Outcome Stability (Discharge Volatility)")
    st.info("High standard deviations indicate erratic, non-standardized discharge processing timelines.")
    fig_vol = px.area(filtered, x='Date', y='Outcome Stability (7d Std)', color_discrete_sequence=['#f59e0b'])
    fig_vol.update_layout(**plotly_layout, yaxis_title="Volatility (7d Std Dev)")
    st.plotly_chart(fig_vol, use_container_width=True, theme=None)
