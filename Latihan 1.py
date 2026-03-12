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

st.set_page_config(
    page_title="Survey Lot Rumah",  # Inilah yang akan menukar nama pada tab
    page_icon="🏠",                  # Anda boleh letak emoji atau laluan fail gambar
    layout="wide"
)

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
        # --- VIDEO BACKGROUND ---
        if os.path.exists("PASSWORD.mp4"):
            video_base64 = get_video_base64("PASSWORD.mp4")
            st.markdown(f"""
                <style>
                /* Menetapkan video sebagai background */
                .stApp {{
                    background: none;
                }}
                .bg-video {{
                    position: fixed;
                    right: 0;
                    bottom: 0;
                    min-width: 100%;
                    min-height: 100%;
                    z-index: -1;
                    object-fit: cover;
                }}
                </style>
                <video autoplay loop muted playsinline class="bg-video">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                </video>
            """, unsafe_allow_html=True)

        _, col_mid, _ = st.columns([1, 1.5, 1])
        with col_mid:
            # --- KOTAK LOGIN SOLID ---
            st.markdown("""
                <div style="background-color: #ffffff; padding: 30px; border-radius: 15px; 
                            box-shadow: 0 8px 20px rgba(0,0,0,0.3); margin-top: 50px;">
                    <h2 style='text-align: center; color: #333;'>Survey Lot Rumah</h2>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                user_id = st.text_input("👤 Masukkan ID:", key="user_id")
                password = st.text_input("🔑 Masukkan Kata Laluan:", type="password", key="user_pass")
                st.markdown("<br>", unsafe_allow_html=True)
                
                submit_button = st.form_submit_button("Log Masuk", use_container_width=True)
                
                if submit_button:
                    if user_id == "67" and password == "ikmalkacak":
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("😕 ID atau Kata Laluan salah.")
            
            if st.button("❓ Lupa Kata Laluan?", use_container_width=True):
                reset_password_dialog()
                
            st.markdown("</div>", unsafe_allow_html=True) # Tutup div kotak login
            
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
        st.sidebar.error(f"⚠️ Masalah profil: Pastikan fail BACKGROUND.mp4 & ICON.png ada di GitHub.")

    # --- ⚙️ FUNGSI SIDEBAR TAMBAHAN ---
    st.sidebar.markdown("---")
    
    # 1. Butang Tukar Kata Laluan
    if st.sidebar.button("🔐 Tukar Kata Laluan", use_container_width=True):
        reset_password_dialog()
        
    # 2. Butang Log Keluar
    if st.sidebar.button("🚪 Log Keluar", use_container_width=True):
        del st.session_state["password_correct"]
        st.rerun()

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
                position: relative; z-index: 1; display: flex; align-items: center;
                padding: 20px; width: 100%;
            }}
            .header-logo {{ width: 100px; margin-right: 25px; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5)); }}
            .header-text-container {{ color: white; }}
            .header-title-main {{ font-size: 38px; font-weight: 800; text-shadow: 2px 2px 8px rgba(0,0,0,0.8); margin: 0; }}
            .header-subtitle-main {{ font-size: 16px; opacity: 0.9; margin: 0; }}
            </style>
            
            <div class="header-container">
                <video autoplay loop muted playsinline class="video-bg">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                </video>
                <div class="header-content">
                    <img src="data:image/png;base64,{logo_base64}" class="header-logo">
                    <div class="header-text-container">
                        <h1 class="header-title-main">SISTEM SURVEY LOT RUMAH</h1>
                        <p class="header-subtitle-main">Politeknik Ungku Omar | Jabatan Kejuruteraan Awam</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ Fail 'VIDEO.mp4' tidak dijumpai untuk paparan header.")
    
    st.markdown("<hr style='border: 1px solid #eee; margin-top: 0px;'>", unsafe_allow_html=True)

    # ================== SIDEBAR SETTINGS ==================
    st.sidebar.header("⚙️ Paparan Fail")
    uploaded_file = st.sidebar.file_uploader("Upload fail CSV", type=["csv"])

    st.sidebar.markdown("---")
    st.sidebar.subheader("🌍 Suiz Peta ")
    
    if "show_map" not in st.session_state:
        st.session_state.show_map = False
        
    show_interactive_map = st.sidebar.toggle("On/Off Peta Satelit", value=st.session_state.show_map)
    st.session_state.show_map = show_interactive_map
    
    map_provider = st.sidebar.radio("Pilih Jenis Peta:", ["Satelit (Hybrid)", "Standard Map"], disabled=not show_interactive_map)

    # --- PILIHAN WARNA ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Jenis Warna")
    poly_color = st.sidebar.color_picker("Warna Kawasan (Poligon)", "#6036AF") 
    line_color = st.sidebar.color_picker("Warna Garisan Sempadan", "#FFFF00") 
    poly_opacity = st.sidebar.slider("Kelegapan Kawasan", 0.0, 1.0, 0.3)

    st.sidebar.markdown("---")
    plot_theme = st.sidebar.selectbox("Tema Warna Pelan Matplotlib", ["Light Mode", "Dark Mode", "Blueprint"])
    show_bg_grid = st.sidebar.checkbox("Papar Grid Latar", value=True)
    grid_interval = st.sidebar.slider("Jarak Selang Grid", 5, 50, 10)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🖋️ Label Kretiviti")
    show_luas_label = st.sidebar.checkbox("Papar Label LUAS", value=True)
    label_size_stn = st.sidebar.slider("Saiz Bulatan Stesen", 15, 30, 22) 
    label_size_data = st.sidebar.slider("Saiz Bearing/Jarak", 5, 12, 7)
    label_size_luas = st.sidebar.slider("Saiz Tulisan LUAS", 8, 30, 14) 
    dist_offset = st.sidebar.slider("Jarak Label Stesen ke Luar", 0.5, 5.0, 1.5)

    # ================== BACA DATA ==================
  # ================== BACA DATA ==================
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            if all(col in df.columns for col in ['STN', 'E', 'N']):
                
                transformer = Transformer.from_crs("EPSG:4390", "EPSG:4326", always_xy=True)
                df['lon'], df['lat'] = transformer.transform(df['E'].values, df['N'].values)
                
                coords_en = list(zip(df['E'], df['N']))
                coords_ll = list(zip(df['lon'], df['lat']))
                poly_geom = Polygon(coords_en)
                poly_ll = Polygon(coords_ll) 
                line_geom = LineString(coords_en + [coords_en[0]])
                centroid_m = poly_geom.centroid
                area = poly_geom.area

                # --- 💾 EKSPORT QGIS ---
                st.sidebar.markdown("---")
                st.sidebar.subheader("💾 Eksport Data")
                
                features = []
                # ... (Kod bahagian features anda kekal sama) ...
                features.append({
                    "type": "Feature",
                    "geometry": mapping(poly_ll),
                    "properties": {"Layer": "Lot_Kawasan", "Area_sqm": round(area, 2), "Perimeter": round(line_geom.length, 2)}
                })
                
                for i in range(len(df)):
                    p1, p2 = df.iloc[i], df.iloc[(i + 1) % len(df)]
                    dE, dN = p2['E'] - p1['E'], p2['N'] - p1['N']
                    dist, bear = np.sqrt(dE**2 + dN**2), (np.degrees(np.arctan2(dE, dN)) + 360) % 360
                    line_seg = LineString([(p1['lon'], p1['lat']), (p2['lon'], p2['lat'])])
                    features.append({
                        "type": "Feature",
                        "geometry": mapping(line_seg),
                        "properties": {"Layer": "Sempadan", "From_Stn": int(p1['STN']), "To_Stn": int(p2['STN']), "Bearing": format_dms(bear), "Distance": round(dist, 3)}
                    })
                
                for i in range(len(df)):
                    pt = Point(df.iloc[i]['lon'], df.iloc[i]['lat'])
                    features.append({
                        "type": "Feature",
                        "geometry": mapping(pt),
                        "properties": {"Layer": "Batu_Sempadan", "label": str(int(df.iloc[i]['STN'])), "Station_ID": int(df.iloc[i]['STN']), "Easting": round(df.iloc[i]['E'], 3), "Northing": round(df.iloc[i]['N'], 3)}
                    })

                geojson_dict = {"type": "FeatureCollection", "features": features}
                st.sidebar.download_button(label="🚀 Export to QGIS (.geojson)", data=json.dumps(geojson_dict), file_name="survey_lot_qgis.geojson", mime="application/json", use_container_width=True)

                st.markdown("---")

                # --- PAPARAN PETA ATAU PLOT ---
                if show_interactive_map:
                    # [Kod Folium anda...]
                    # Pastikan tiada st.rerun() di sini
                    google_map_url = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
                    if map_provider == "Standard Map":
                        google_map_url = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'

                    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=20, max_zoom=22, tiles=google_map_url, attr='Google')
                    # ... (selebihnya kod folium anda) ...
                    st_folium(m, width=1400, height=600, key="peta_survey")

                else:
                    # --- MOD MATPLOTLIB ---
                    # [Kod Matplotlib anda...]
                    if plot_theme == "Dark Mode": bg_color, grid_color = "#121212", "#555555"
                    elif plot_theme == "Blueprint": bg_color, grid_color = "#003366", "#004080"
                    else: bg_color, grid_color = "#ffffff", "#aaaaaa"
                    # ... (selebihnya kod plot anda) ...
                    fig, ax = plt.subplots(figsize=(10, 8))
                    st.pyplot(fig)

            else: 
                st.error("❌ Kolum STN, E, N tak jumpa dalam CSV!")

        except Exception as e: 
            st.error(f"❌ Ada ralat: {e}")









