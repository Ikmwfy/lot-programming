import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, Point, LineString, mapping
import json
import os
import folium
from streamlit_folium import st_folium
from pyproj import Transformer
import base64

# --- SETTING PAGE ---
st.set_page_config(layout="wide")

def get_video_base64(video_file):
    with open(video_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def format_dms(decimal_degree):
    d = int(decimal_degree)
    m = int((decimal_degree - d) * 60)
    s = round((((decimal_degree - d) * 60) - m) * 60, 0)
    return f"{d}°{abs(m):02d}'{abs(int(s)):02d}\""

@st.dialog("🔑 Kemaskini Kata Laluan")
def reset_password_dialog():
    st.info("Sila sahkan ID untuk menetapkan semula kata laluan.")
    id_sah = st.text_input("Sahkan ID Pengguna:")
    pass_baru = st.text_input("Kata Laluan Baharu:", type="password")
    pass_sah = st.text_input("Sahkan Kata Laluan Baharu:", type="password")
    if st.button("Simpan Kata Laluan", use_container_width=True):
        if id_sah == "ikmalkacak" and pass_baru == pass_sah and pass_baru != "":
            st.success("✅ Kata laluan berjaya dikemaskini!")
            st.rerun()
        else:
            st.error("❌ Maklumat tidak sepadan.")

def check_password():
    if "password_correct" not in st.session_state:
        _, col_mid, _ = st.columns([1, 1.5, 1])
        with col_mid:
            st.markdown("<h2 style='text-align: center;'>Survey Lot Rumah</h2>", unsafe_allow_html=True)
            user_id = st.text_input("👤 Masukkan ID:", key="user_id")
            password = st.text_input("🔑 Masukkan Kata Laluan:", type="password", key="user_pass")
            if st.button("Log Masuk", use_container_width=True):
                if user_id == "67" and password == "ikmalkacak":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("😕 ID atau Kata Laluan salah.")
            if st.button("❓ Lupa Kata Laluan?", use_container_width=True):
                reset_password_dialog()
        return False
    return True

if check_password():
    video_path = "VIDEO.mp4" 
    logo_path = "PUO.png"

    # --- SIDEBAR ---
    try:
        bg_video_base64 = get_video_base64("BACKGROUND.mp4")
        with open("ICON.jpeg", "rb") as f:
            icon_base64 = base64.b64encode(f.read()).decode()
        st.sidebar.markdown(f"""
            <div class="sidebar-profile-container">
                <video autoplay loop muted playsinline class="sidebar-video-bg">
                    <source src="data:video/mp4;base64,{bg_video_base64}" type="video/mp4">
                </video>
                <div class="sidebar-profile-content">
                    <div class="icon-wrapper"><img src="data:image/png;base64,{icon_base64}" class="sidebar-icon"></div>
                    <h3 style="color: white; margin-top: 10px;">Hai, Malfoy!</h3>
                    <p style="color: #00d4ff;">Student</p>
                </div>
            </div>
            <style>
            .sidebar-profile-container {{ position: relative; width: 100%; height: 230px; border-radius: 20px; overflow: hidden; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); }}
            .sidebar-video-bg {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0; }}
            .sidebar-profile-content {{ position: relative; z-index: 1; padding-top: 30px; background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.7)); height: 100%; }}
            .icon-wrapper {{ display: inline-block; width: 100px; height: 100px; background: rgba(255, 255, 255, 0.2); border-radius: 50%; overflow: hidden; border: 3px solid white; }}
            .sidebar-icon {{ width: 100%; height: 100%; object-fit: cover; transform: scale(1.3); }}
            </style>
        """, unsafe_allow_html=True)
    except:
        st.sidebar.error("⚠️ Fail profil tiada.")

    # --- MAIN HEADER ---
    if os.path.exists(video_path):
        video_base64 = get_video_base64(video_path)
        logo_base64 = base64.b64encode(open(logo_path, "rb").read()).decode() if os.path.exists(logo_path) else ""
        st.markdown(f"""
            <div class="header-container">
                <video autoplay loop muted playsinline class="video-bg">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                </video>
                <div class="header-content">
                    <img src="data:image/png;base64,{logo_base64}" class="header-logo">
                    <div class="header-text-container">
                        <h1 class="header-title-main">SISTEM SURVEY LOT RUMAH</h1>
                        <p class="header-subtitle-main">Politeknik Ungku Omar | JKA</p>
                    </div>
                </div>
            </div>
            <style>
            .header-container {{ position: relative; width: 110%; height: 180px; overflow: hidden; border-radius: 15px; margin-bottom: 25px; margin-left: -50px; background-color: #000; display: flex; align-items: center; }}
            .video-bg {{ position: absolute; top: 50%; left: 0; min-width: 100%; min-height: 100%; z-index: 0; transform: translateY(-50%); opacity: 0.6; }}
            .header-content {{ position: relative; z-index: 1; display: flex; align-items: center; padding: 20px; }}
            .header-logo {{ width: 100px; margin-right: 25px; }}
            .header-title-main {{ font-size: 38px; color: white; margin: 0; }}
            .header-subtitle-main {{ font-size: 16px; color: white; margin: 0; }}
            </style>
        """, unsafe_allow_html=True)

    # --- SIDEBAR OPTIONS ---
    st.sidebar.header("⚙️ Tetapan")
    uploaded_file = st.sidebar.file_uploader("Upload fail CSV", type=["csv"])
    if "show_map" not in st.session_state: st.session_state.show_map = False
    show_interactive_map = st.sidebar.toggle("On/Off Peta Satelit", value=st.session_state.show_map)
    st.session_state.show_map = show_interactive_map
    map_provider = st.sidebar.radio("Pilih Jenis Peta:", ["Satelit (Hybrid)", "Standard Map"], disabled=not show_interactive_map)
    poly_color = st.sidebar.color_picker("Warna Kawasan", "#6036AF") 
    line_color = st.sidebar.color_picker("Warna Garisan", "#FFFF00") 
    poly_opacity = st.sidebar.slider("Kelegapan", 0.0, 1.0, 0.3)
    plot_theme = st.sidebar.selectbox("Tema Matplotlib", ["Light Mode", "Dark Mode", "Blueprint"])
    show_bg_grid = st.sidebar.checkbox("Grid", value=True)
    grid_interval = st.sidebar.slider("Jarak Grid", 5, 50, 10)
    show_luas_label = st.sidebar.checkbox("Label LUAS", value=True)
    label_size_stn = st.sidebar.slider("Saiz Stesen", 15, 30, 22) 
    label_size_data = st.sidebar.slider("Saiz Bearing", 5, 12, 7)
    label_size_luas = st.sidebar.slider("Saiz Luas", 8, 30, 14)

    # --- DATA PROCESSING ---
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if all(col in df.columns for col in ['STN', 'E', 'N']):
                trans = Transformer.from_crs("EPSG:4390", "EPSG:4326", always_xy=True)
                df['lon'], df['lat'] = trans.transform(df['E'].values, df['N'].values)
                poly = Polygon(list(zip(df['E'], df['N'])))
                area = poly.area
                
                if show_interactive_map:
                    # Folium Logic Here
                    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=20)
                    folium.Polygon(list(zip(df['lat'], df['lon'])), color=line_color, fill_color=poly_color).add_to(m)
                    st_folium(m, width=1400, height=600)
                else:
                    # Matplotlib Logic Here
                    fig, ax = plt.subplots()
                    ax.plot(*(poly.exterior.xy), color=line_color)
                    st.pyplot(fig)
            else:
                st.error("❌ Kolum tidak cukup.")
        except Exception as e:
            st.error(f"❌ Ralat: {e}")
