import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, Point, LineString
import json
import os

# ================== FUNGSI TUKAR DMS ==================
def format_dms(decimal_degree):
    d = int(decimal_degree)
    m = int((decimal_degree - d) * 60)
    s = round((((decimal_degree - d) * 60) - m) * 60, 0)
    return f"{d}°{abs(m):02d}'{abs(int(s)):02d}\""

# ================== FUNGSI LOGIN ==================
def check_password():

    USER_ID = "1"
    USER_PASS = "admin123"

    st.markdown("""
    <style>

    .stApp{
        background-color:#0b1220;
    }

    .title{
        text-align:center;
        font-size:42px;
        font-weight:700;
        color:white;
        margin-bottom:40px;
    }

    .login-box{
        max-width:700px;
        margin:auto;
        background-color:#0f172a;
        padding:40px;
        border-radius:12px;
        box-shadow:0px 0px 20px rgba(0,0,0,0.5);
    }

    div[data-testid="stTextInput"] input{
        background-color:#1e293b;
        color:white;
        border-radius:10px;
        border:1px solid #334155;
        height:45px;
    }

    div[data-testid="stButton"] button{
        height:45px;
        border-radius:10px;
        font-weight:600;
        background-color:#111827;
        color:white;
        border:1px solid #334155;
    }

    div[data-testid="stButton"] button:hover{
        border:1px solid #6366f1;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="title">🔐 Sistem Survey Lot PUO</div>', unsafe_allow_html=True)

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        st.markdown("👤 **Masukkan ID:**")
        user_id = st.text_input("", key="login_id")

        st.markdown("🔑 **Masukkan Kata Laluan:**")
        password = st.text_input("", type="password", key="login_pass")

        login = st.button("Log Masuk", use_container_width=True)

        if login:

            if user_id == USER_ID and password == USER_PASS:

                st.session_state["password_correct"] = True
                st.session_state["nama"] = "Admin"
                st.rerun()

            else:

                st.error("ID atau Kata Laluan Salah")

        st.button("❓ Lupa Kata Laluan?", use_container_width=True)

    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return True
    else:
        return False
        
# ================== MAIN APP ==================
if check_password():
    # Set config halaman
    st.set_page_config(page_title="Visualisasi Poligon Pro", layout="wide")

    # --- PENYELESAIAN LOGO ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "puo.png")

    col_logo, col_text = st.columns([1, 8])

    with col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, width=120)
        else:
            try:
                st.image("puo.png", width=120)
            except:
                st.markdown("⚠️ **Logo tidak dijumpai**")

    with col_text:
        st.title("POLITEKNIK UNGKU OMAR")
        st.caption("Paparan poligon tanah dengan Grid Latar Belakang (Dashed)")

    # ================== SIDEBAR ==================
    st.sidebar.header("⚙️ Tetapan Paparan")
    uploaded_file = st.sidebar.file_uploader("Upload fail CSV", type=["csv"])

    st.sidebar.markdown("---")
    plot_theme = st.sidebar.selectbox("Tema Warna Pelan", ["Light Mode", "Dark Mode", "Blueprint"])
    show_bg_grid = st.sidebar.checkbox("Papar Grid Latar (Macam Gambar)", value=True)
    grid_interval = st.sidebar.slider("Jarak Selang Grid", 5, 50, 10)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🖋️ Gaya Label")
    label_size_stn = st.sidebar.slider("Saiz Label Stesen", 6, 16, 10)
    label_size_data = st.sidebar.slider("Saiz Bearing/Jarak", 5, 12, 7)
    
    # FEATURE BARU: Slider untuk ubah saiz tulisan "LUAS"
    label_size_luas = st.sidebar.slider("Saiz Tulisan LUAS", 8, 30, 12) 
    
    dist_offset = st.sidebar.slider("Jarak Label Stesen ke Luar", 0.5, 5.0, 1.5)

    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Eksport QGIS")

    # ================== BACA DATA ==================
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

        # Generate Geometri
        coords = list(zip(df['E'], df['N']))
        poly_geom = Polygon(coords)
        line_geom = LineString(coords + [coords[0]])
        centroid = poly_geom.centroid
        area = poly_geom.area

        # --- PENYEDIAAN DATA QGIS ---
        poly_feature = {"type": "Feature", "properties": {"Jenis": "Kawasan", "Luas_m2": round(area, 3)}, "geometry": poly_geom.__geo_interface__}
        line_feature = {"type": "Feature", "properties": {"Jenis": "Sempadan"}, "geometry": line_geom.__geo_interface__}
        stn_features = [{"type": "Feature", "properties": {"STN": int(r['STN'])}, "geometry": Point(r['E'], r['N']).__geo_interface__} for _, r in df.iterrows()]
        combined_geojson = {"type": "FeatureCollection", "features": [poly_feature, line_feature] + stn_features}
        
        st.sidebar.download_button("📥 Download GeoJSON", json.dumps(combined_geojson), "pelan_lengkap.geojson", "application/json")

        # ================== METRIC ==================
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Luas (m²)", f"{area:.2f}")
        col2.metric("Luas (Ekar)", f"{area/4046.856:.4f}")
        col3.metric("Bilangan Stesen", len(df))
        col4.metric("Status", "Tutup" if poly_geom.is_valid else "Ralat")

        # ================== PLOT (MATPLOTLIB) ==================
        if plot_theme == "Dark Mode":
            bg_color, grid_color, text_color, line_c = "#121212", "#555555", "white", "cyan"
        elif plot_theme == "Blueprint":
            bg_color, grid_color, text_color, line_c = "#003366", "#004080", "white", "yellow"
        else:
            bg_color, grid_color, text_color, line_c = "#ffffff", "#aaaaaa", "black", "black"

        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        # Plot Garisan Sempadan
        ax.plot(*(line_geom.xy), linewidth=2, color=line_c, zorder=4)
        ax.fill(*(poly_geom.exterior.xy), color='green', alpha=0.1, zorder=1)

        # Grid Latar Belakang
        if show_bg_grid:
            min_e, min_n, max_e, max_n = poly_geom.bounds
            ax.set_xlim(np.floor(min_e/10)*10 - 20, np.ceil(max_e/10)*10 + 20)
            ax.set_ylim(np.floor(min_n/10)*10 - 20, np.ceil(max_n/10)*10 + 20)
            ax.grid(True, which='both', color=grid_color, linestyle='--', linewidth=0.8, alpha=0.7, zorder=0)
            ax.xaxis.set_major_locator(plt.MultipleLocator(grid_interval))
            ax.yaxis.set_major_locator(plt.MultipleLocator(grid_interval))
        else:
            ax.axis('off')

        # PAPARAN TULISAN LUAS (DENGAN SAIZ DINAMIK)
        ax.text(centroid.x, centroid.y, f"LUAS\n{area:.2f} m²", 
                fontsize=label_size_luas, # <--- Menggunakan saiz dari slider
                fontweight='bold', 
                color='darkgreen', 
                ha='center',
                bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.9, ec='green'), 
                zorder=10)

        # Plot Label Bearing, Jarak dan No Stesen
        for i in range(len(df)):
            p1, p2 = df.iloc[i], df.iloc[(i + 1) % len(df)]
            dE, dN = p2['E'] - p1['E'], p2['N'] - p1['N']
            dist, bear = np.sqrt(dE**2 + dN**2), (np.degrees(np.arctan2(dE, dN)) + 360) % 360
            
            # Kira sudut pusingan teks supaya selari dengan garisan
            txt_angle = np.degrees(np.arctan2(dN, dE))
            if txt_angle > 90: txt_angle -= 180
            if txt_angle < -90: txt_angle += 180
            
            # Label Bearing & Jarak
            ax.text((p1['E']+p2['E'])/2, (p1['N']+p2['N'])/2, f"{format_dms(bear)}\n{dist:.2f}m", 
                    fontsize=label_size_data, color='brown', fontweight='bold', ha='center', rotation=txt_angle,
                    bbox=dict(boxstyle='round,pad=0.1', fc=bg_color, alpha=0.4, ec='none'), zorder=6)

            # Label Nombor Stesen (Offset ke luar)
            ve, vn = p1['E'] - centroid.x, p1['N'] - centroid.y
            mag = np.sqrt(ve**2 + vn**2)
            ax.text(p1['E'] + (ve/mag)*dist_offset, p1['N'] + (vn/mag)*dist_offset, 
                    str(int(p1['STN'])), fontsize=label_size_stn, fontweight='bold', color='blue', ha='center', zorder=7)
            
            # Titik Stesen (Point)
            ax.scatter(p1['E'], p1['N'], color='red', s=50, edgecolors='black', zorder=8)

        ax.set_aspect("equal", adjustable="box")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Ralat: Sila pastikan format CSV betul (E, N, STN). Ralat teknikal: {e}")
