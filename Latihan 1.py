 import streamlit as st

import pandas as pd

import matplotlib.pyplot as plt

import numpy as np

from shapely.geometry import Polygon, Point, LineString

import json

import os

import contextily as cx 

import base64


# Set config halaman

st.set_page_config(page_title="Survey Lot Rumah", layout="wide")


# Fungsi untuk menukar video ke base64 supaya boleh dimainkan dalam HTML

def get_video_base64(video_path):

    with open(video_path, "rb") as f:

        data = f.read()

    return base64.b64encode(data).decode()


# ================== FUNGSI TUKAR DMS ==================

def format_dms(decimal_degree):

    d = int(decimal_degree)

    m = int((decimal_degree - d) * 60)

    s = round((((decimal_degree - d) * 60) - m) * 60, 0)

    return f"{d}°{abs(m):02d}'{abs(int(s)):02d}\""


# ================== FUNGSI LOGIN ==================

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


# ================== LOGIK SESSION STATE ==================

if "password_correct" not in st.session_state:

    st.session_state["password_correct"] = False


if not st.session_state["password_correct"]:

    login_screen()

    st.stop()


# ================== MAIN APP ==================


current_dir = os.path.dirname(os.path.abspath(__file__))

logo_path = os.path.join(current_dir, "PUO.png")

video_path = os.path.join(current_dir, "VIDEO.mp4")


# ================== HEADER VISUAL BERGERAK (VIDEO) ==================

if os.path.exists(video_path):

    video_base64 = get_video_base64(video_path)

    

    # CSS untuk video background dalam header

    st.markdown(f"""

        <style>

        .header-container {{

            position: relative;

            width: 100%;

            height: 180px;

            overflow: hidden;

            border-radius: 15px;

            margin-bottom: 25px;

            display: flex;

            align-items: center;

            background-color: #000;

        }}

        .video-bg {{

            position: absolute;

            top: 50%;

            left: 50%;

            min-width: 100%;

            min-height: 100%;

            width: auto;

            height: auto;

            z-index: 0;

            transform: translate(-50%, -50%);

            opacity: 0.6; /* Gelapkan sedikit video supaya teks jelas */

        }}

        .header-content {{

            position: relative;

            z-index: 1;

            display: flex;

            align-items: center;

            padding: 20px;

            width: 100%;

        }}

        .header-logo {{

            width: 100px;

            margin-right: 25px;

            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));

        }}

        .header-text-container {{

            color: white;

        }}

        .header-title-main {{

            font-size: 38px;

            font-weight: 800;

            text-shadow: 2px 2px 8px rgba(0,0,0,0.8);

            margin: 0;

        }}

        .header-subtitle-main {{

            font-size: 16px;

            opacity: 0.9;

            margin: 0;

        }}

        </style>

        

        <div class="header-container">

            <video autoplay loop muted playsinline class="video-bg">

                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">

            </video>

            <div class="header-content">

                <img src="data:image/png;base64,{base64.b64encode(open(logo_path, "rb").read()).decode() if os.path.exists(logo_path) else ''}" class="header-logo">

                <div class="header-text-container">

                    <h1 class="header-title-main">SISTEM SURVEY LOT RUMAH</h1>

                    <p class="header-subtitle-main">Politeknik Ungku Omar | Jabatan Kejuruteraan Awam</p>

                </div>

            </div>

        </div>

    """, unsafe_allow_html=True)

else:

    st.error("Fail VIDEO.mp4 tidak dijumpai dalam folder.")


# ================== SIDEBAR ==================

st.sidebar.header("⚙️ Tetapan Paparan")

uploaded_file = st.sidebar.file_uploader("Upload fail CSV", type=["csv"])


st.sidebar.markdown("---")

plot_theme = st.sidebar.selectbox("Tema Warna Pelan", ["Light Mode", "Dark Mode", "Blueprint", "Google Satellite"])

show_bg_grid = st.sidebar.checkbox("Papar Grid Latar", value=True)

grid_interval = st.sidebar.slider("Jarak Selang Grid", 5, 50, 10)


st.sidebar.markdown("---")

st.sidebar.subheader("🖋️ Gaya Label")

label_size_stn = st.sidebar.slider("Saiz Label Stesen", 6, 16, 10)

label_size_data = st.sidebar.slider("Saiz Bearing/Jarak", 5, 12, 7)

label_size_luas = st.sidebar.slider("Saiz Tulisan LUAS", 8, 30, 12) 

dist_offset = st.sidebar.slider("Jarak Label Stesen ke Luar", 0.5, 5.0, 1.5)


if st.sidebar.button("Log Keluar"):

    st.session_state["password_correct"] = False

    st.rerun()


# ================== BACA DATA & PLOT (BAHAGIAN SETERUSNYA KEKAL SAMA) ==================

try:

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

    else:

        data_path = os.path.join(current_dir, "data ukur.csv")

        if os.path.exists(data_path):

            df = pd.read_csv(data_path)

        else:

            st.info("Sila upload fail CSV untuk bermula.")

            st.stop()


    coords = list(zip(df['E'], df['N']))

    poly_geom = Polygon(coords)

    line_geom = LineString(coords + [coords[0]])

    centroid = poly_geom.centroid

    area = poly_geom.area


    # Metric

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Luas (m²)", f"{area:.2f}")

    col2.metric("Luas (Ekar)", f"{area/4046.856:.4f}")

    col3.metric("Bilangan Stesen", len(df))

    col4.metric("Status", "Tutup" if poly_geom.is_valid else "Ralat")


    # Plot Logic

    if plot_theme == "Dark Mode":

        bg_color, grid_color, text_color, line_c = "#121212", "#555555", "white", "cyan"

    elif plot_theme == "Blueprint":

        bg_color, grid_color, text_color, line_c = "#003366", "#004080", "white", "yellow"

    elif plot_theme == "Google Satellite":

        bg_color, grid_color, text_color, line_c = "black", "white", "white", "#00FF00"

    else:

        bg_color, grid_color, text_color, line_c = "#ffffff", "#aaaaaa", "black", "black"


    fig, ax = plt.subplots(figsize=(10, 8))

    fig.patch.set_facecolor(bg_color)

    ax.set_facecolor(bg_color)


    ax.plot(*(line_geom.xy), linewidth=2, color=line_c, zorder=4)

    ax.fill(*(poly_geom.exterior.xy), color='green', alpha=0.1, zorder=1)


    min_e, min_n, max_e, max_n = poly_geom.bounds

    ax.set_xlim(min_e - 30, max_e + 30)

    ax.set_ylim(min_n - 30, max_n + 30)


    if plot_theme == "Google Satellite":

        try:

            cx.add_basemap(ax, crs="EPSG:4390", source=cx.providers.Esri.WorldImagery, zorder=0)

        except:

            st.sidebar.error("Gagal memuatkan imej satelit.")


    if show_bg_grid:

        ax.grid(True, color=grid_color, linestyle='--', alpha=0.5)

        ax.xaxis.set_major_locator(plt.MultipleLocator(grid_interval))

        ax.yaxis.set_major_locator(plt.MultipleLocator(grid_interval))

    else:

        ax.axis('off')


    ax.text(centroid.x, centroid.y, f"LUAS\n{area:.2f} m²", fontsize=label_size_luas, fontweight='bold', color='darkgreen', ha='center', bbox=dict(boxstyle='round', fc='white', alpha=0.9))


    for i in range(len(df)):

        p1, p2 = df.iloc[i], df.iloc[(i + 1) % len(df)]

        dE, dN = p2['E'] - p1['E'], p2['N'] - p1['N']

        dist, bear = np.sqrt(dE**2 + dN**2), (np.degrees(np.arctan2(dE, dN)) + 360) % 360

        txt_angle = np.degrees(np.arctan2(dN, dE))

        if txt_angle > 90: txt_angle -= 180

        if txt_angle < -90: txt_angle += 180

        

        ax.text((p1['E']+p2['E'])/2, (p1['N']+p2['N'])/2, f"{format_dms(bear)}\n{dist:.2f}m", fontsize=label_size_data, color='brown', ha='center', rotation=txt_angle)

        

        ve, vn = p1['E'] - centroid.x, p1['N'] - centroid.y

        mag = np.sqrt(ve**2 + vn**2)

        ax.text(p1['E'] + (ve/mag)*dist_offset, p1['N'] + (vn/mag)*dist_offset, str(int(p1['STN'])), fontsize=label_size_stn, color='blue', ha='center')

        ax.scatter(p1['E'], p1['N'], color='red', s=50, edgecolors='white', zorder=8)


    ax.set_aspect("equal")

    st.pyplot(fig)


except Exception as e:

    st.error(f"Sila pastikan format CSV betul. Ralat: {e}") 
