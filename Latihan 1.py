import streamlit as st
# ... import yang lain ...

st.set_page_config(layout="wide") # TAMBAH BARIS INI
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

def get_video_base64(video_file):
    with open(video_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ================== FUNGSI TUKAR DMS ==================
def format_dms(decimal_degree):
    d = int(decimal_degree)
    m = int((decimal_degree - d) * 60)
    s = round((((decimal_degree - d) * 60) - m) * 60, 0)
    return f"{d}°{abs(m):02d}'{abs(int(s)):02d}\""

# ================== FUNGSI LOGIN & KEMASKINI ==================
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
            st.error("❌ Maklumat tidak sepadan atau kosong.")

def check_password():
    if "password_correct" not in st.session_state:
        _, col_mid, _ = st.columns([1, 1.5, 1])
        with col_mid:
            st.markdown("<h2 style='text-align: center;'>Survey Lot Rumah</h2>", unsafe_allow_html=True)
            user_id = st.text_input("👤 Masukkan ID:", key="user_id")
            password = st.text_input("🔑 Masukkan Kata Laluan:", type="password", key="user_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            
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

# ================== MAIN APP (SELEPAS LOGIN) ==================
if check_password():
    
    # Tetapan laluan fail
    video_path = "VIDEO.mp4"
    logo_path = "PUO.png"

    # --- 👤 PROFIL PENGGUNA (SIDEBAR) ---
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
                    <div class="icon-wrapper">
                        <img src="data:image/png;base64,{icon_base64}" class="sidebar-icon">
                    </div>
                    <h3 style="color: white; margin-top: 10px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">Hai, Malfoy!</h3>
                    <p style="color: #00d4ff; font-size: 0.9em; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">Student</p>
                </div>
            </div>
            
            <style>
            .sidebar-profile-container {{
                position: relative;
                width: 100%;
                height: 230px;
                border-radius: 20px;
                overflow: hidden;
                text-align: center;
                margin-bottom: 25px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.1);
            }}

            .sidebar-video-bg {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                z-index: 0;
            }}

            .sidebar-profile-content {{
                position: relative;
                z-index: 1;
                padding-top: 30px;
                background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.7));
                height: 100%;
            }}

            .icon-wrapper {{
                display: inline-block;
                width: 100px;
                height: 100px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                overflow: hidden;
                border: 3px solid white;
                box-shadow: 0 0 15px rgba(255,255,255,0.5);
                backdrop-filter: blur(5px);
            }}

            .sidebar-icon {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                transform: scale(1.3);
                display: block;
            }}
            </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.error("⚠️ Masalah profil: Pastikan fail BACKGROUND.mp4 & ICON.png ada di GitHub.")

    # --- HEADER VISUAL BERGERAK (VIDEO) ---
    if os.path.exists(video_path):
        video_base64 = get_video_base64(video_path)

        logo_base64 = ""
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode()

        st.markdown(f"""
        <style>
        .header-container {{
            position: relative;
            width: 110%;
            height: 180px;
            overflow: hidden;
            border-radius: 15px;
            margin-bottom: 25px;
            margin-left: -50px;
            background-color: #000;
            display: flex;
            align-items: center;
        }}
        .video-bg {{
            position: absolute;
            top: 50%;
            left: 0;
            min-width: 100%;
            min-height: 100%;
            width: auto;
            height: auto;
            z-index: 0;
            transform: translateY(-50%);
            opacity: 0.6;
        }}
        .header-content {{
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            padding: 20px;
            width: 100%;
        }}
        .header-logo {{ width: 100px; margin-right: 25px; }}
        .header-title-main {{ font-size: 38px; font-weight: 800; color:white; margin:0; }}
        .header-subtitle-main {{ font-size: 16px; color:white; margin:0; }}
        </style>

        <div class="header-container">
            <video autoplay loop muted playsinline class="video-bg">
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            </video>
            <div class="header-content">
                <img src="data:image/png;base64,{logo_base64}" class="header-logo">
                <div>
                    <h1 class="header-title-main">SISTEM SURVEY LOT RUMAH</h1>
                    <p class="header-subtitle-main">Politeknik Ungku Omar | Jabatan Kejuruteraan Awam</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("⚠️ Fail 'VIDEO.mp4' tidak dijumpai untuk paparan header.")
