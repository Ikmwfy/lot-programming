import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, Point, LineString
import json
import os
import contextily as cx 
import base64

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Survey Lot PUO", layout="wide")

# Fungsi Helper
def get_file_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def format_dms(decimal_degree):
    d = int(decimal_degree)
    m = int((decimal_degree - d) * 60)
    s = round((((decimal_degree - d) * 60) - m) * 60, 0)
    return f"{d}°{abs(m):02d}'{abs(int(s)):02d}\""

# Fungsi Login
def login_screen():
    USER_ID = "1"
    USER_PASS = "ikmalkacak"
    st.markdown("""
    <style>
    .stApp{ background-color:#0b1220; }
    .login-title{ text-align:center; font-size:42px; font-weight:700; color:white; margin-bottom:40px; }
    div[data-testid="stTextInput"] input{ background-color:#1e293b; color:white; border-radius:10px; border:1px solid #334155; height:45px; }
    div[data-testid="stButton"] button{ height:45px; border-radius:10px; font-weight:600; background-color:#111827; color:white; border:1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Sistem Survey Lot PUO</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_id = st.text_input("👤 **Masukkan ID:**", key="login_id")
        password = st.text_input("🔑 **Masukkan Kata Laluan:**", type="password", key="login_pass")
        if st.button("Log Masuk", use_container_width=True):
            if user_id == USER_ID and password == USER_PASS:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("ID atau Kata Laluan Salah")

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    login_screen()
    st.stop()

# Main Application
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "puo.png")
video_path = os.path.join(current_dir, "VIDEO.mp4")

# Header dengan Video Latar
video_base64 = get_file_base64(video_path)
logo_base64 = get_file_base64(logo_path)

if video_base64:
    st.markdown(f"""
        <style>
        .header-container {{ position: relative; width: 100%; height: 180px; overflow: hidden; border-radius: 15px; margin-bottom: 25px; display: flex; align-items: center; background-color: #000; }}
        .video-bg {{ position: absolute; top: 50%; left: 50%; min-width: 100%; min-height: 100%; width: auto; height: auto; z-index: 0; transform: translate(-50%, -50%); opacity: 0.6; }}
        .header-content {{ position: relative; z-index: 1; display: flex; align-items: center; padding: 20px; width: 100%; }}
        .header-logo {{ width: 100px; height: auto; margin-right: 25px; object-fit: contain; }}
        .header-title-main {{ font-size: 38px; font-weight: 800; color: white; text-shadow: 2px 2px 8px rgba(0,0,0,0.8); margin: 0; }}
        </style>
        <div class="header-container">
            <video autoplay loop muted playsinline class="video-bg">
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            </video>
            <div class="header-content">
                {'<img src="data:image/png;base64,' + logo_base64 + '" class="header-logo">' if logo_base64 else ''}
                <div class="header-text-container">
                    <h1 class="header-title-main">SISTEM SURVEY LOT RUMAH</h1>
                    <p style="color:white; margin:0;">Politeknik Ungku Omar | Jabatan Kejuruteraan Awam</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ Tetapan Paparan")
uploaded_file = st.sidebar.file_uploader("Upload fail CSV", type=["csv"])
plot_theme = st.sidebar.selectbox("Tema Warna Pelan", ["Light Mode", "Google Satellite"])

# Baca Data
try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv(os.path.join(current_dir, "data ukur.csv"))

    coords = list(zip(df['E'], df['N']))
    poly_geom = Polygon(coords)
    line_geom = LineString(coords + [coords[0]])
    area = poly_geom.area

    # Visualisasi Matplotlib
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Lukis Sempadan Pink (Style GIS)
    ax.plot(*(line_geom.xy), linewidth=3, color='#ff00ff', marker='o', markerfacecolor='red', markersize=8, zorder=4)
    ax.fill(*(poly_geom.exterior.xy), color='#ff00ff', alpha=0.15, zorder=1)

    # Label Stesen
    for i in range(len(df)):
        x, y = df.iloc[i]['E'], df.iloc[i]['N']
        ax.scatter(x, y, color='red', s=200, zorder=5)
        ax.text(x, y, str(int(df.iloc[i]['STN'])), color='white', fontweight='bold', ha='center', va='center', zorder=6)

    # Label Bearing & Jarak
    for i in range(len(df)):
        p1, p2 = df.iloc[i], df.iloc[(i + 1) % len(df)]
        dE, dN = p2['E'] - p1['E'], p2['N'] - p1['N']
        dist, bear = np.sqrt(dE**2 + dN**2), (np.degrees(np.arctan2(dE, dN)) + 360) % 360
        angle = np.degrees(np.arctan2(dN, dE))
        if angle > 90: angle -= 180
        if angle < -90: angle += 180
        ax.text((p1['E']+p2['E'])/2, (p1['N']+p2['N'])/2, f"{format_dms(bear)}\n{dist:.2f}m", 
                color='#ff00ff', fontsize=9, fontweight='bold', ha='center', rotation=angle, zorder=7)

    if plot_theme == "Google Satellite":
        cx.add_basemap(ax, crs="EPSG:4390", source=cx.providers.Esri.WorldImagery, zorder=0)
    
    ax.set_aspect("equal")
    ax.axis('off')
    st.pyplot(fig)

except Exception as e:
    st.error(f"Sila pastikan fail data wujud/format betul. Ralat: {e}")
