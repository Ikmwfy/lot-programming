import streamlit as st
st.set_page_config(layout="wide")

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


# ================== FUNGSI VIDEO ==================
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


# ================== RESET PASSWORD ==================
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


# ================== LOGIN ==================
def check_password():

    if "password_correct" not in st.session_state:

        _, col_mid, _ = st.columns([1, 1.5, 1])

        with col_mid:

            st.markdown(
                "<h2 style='text-align: center;'>Survey Lot Rumah</h2>",
                unsafe_allow_html=True
            )

            user_id = st.text_input("👤 Masukkan ID:", key="user_id")
            password = st.text_input(
                "🔑 Masukkan Kata Laluan:",
                type="password",
                key="user_pass"
            )

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


# ================== MAIN APP ==================
if check_password():

    video_path = "VIDEO.mp4"
    logo_path = "PUO.png"

    # ================== SIDEBAR ==================
    st.sidebar.header("⚙️ Tetapan Paparan")

    uploaded_file = st.sidebar.file_uploader(
        "Upload fail CSV",
        type=["csv"]
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("🌍 Mod Peta Interaktif")

    if "show_map" not in st.session_state:
        st.session_state.show_map = False

    show_interactive_map = st.sidebar.toggle(
        "On/Off Peta Satelit",
        value=st.session_state.show_map
    )

    st.session_state.show_map = show_interactive_map

    map_provider = st.sidebar.radio(
        "Pilih Jenis Peta:",
        ["Satelit (Hybrid)", "Standard Map"],
        disabled=not show_interactive_map
    )

    # ================== WARNA ==================
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Pilihan Warna")

    poly_color = st.sidebar.color_picker(
        "Warna Kawasan (Poligon)",
        "#6036AF"
    )

    line_color = st.sidebar.color_picker(
        "Warna Garisan Sempadan",
        "#FFFF00"
    )

    poly_opacity = st.sidebar.slider(
        "Kelegapan Kawasan",
        0.0,
        1.0,
        0.3
    )

    st.sidebar.markdown("---")

    plot_theme = st.sidebar.selectbox(
        "Tema Warna Pelan Matplotlib",
        ["Light Mode", "Dark Mode", "Blueprint"]
    )

    show_bg_grid = st.sidebar.checkbox(
        "Papar Grid Latar",
        value=True
    )

    grid_interval = st.sidebar.slider(
        "Jarak Selang Grid",
        5,
        50,
        10
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("🖋️ Gaya Label")

    show_luas_label = st.sidebar.checkbox(
        "Papar Label LUAS",
        value=True
    )

    label_size_stn = st.sidebar.slider(
        "Saiz Bulatan Stesen",
        15,
        30,
        22
    )

    label_size_data = st.sidebar.slider(
        "Saiz Bearing/Jarak",
        5,
        12,
        7
    )

    label_size_luas = st.sidebar.slider(
        "Saiz Tulisan LUAS",
        8,
        30,
        14
    )

    # ================== BACA DATA ==================
    if uploaded_file is not None:

        st.session_state.show_map = True

        try:

            df = pd.read_csv(uploaded_file)

            if all(col in df.columns for col in ["STN", "E", "N"]):

                transformer = Transformer.from_crs(
                    "EPSG:4390",
                    "EPSG:4326",
                    always_xy=True
                )

                df["lon"], df["lat"] = transformer.transform(
                    df["E"].values,
                    df["N"].values
                )

                coords_en = list(zip(df["E"], df["N"]))
                coords_ll = list(zip(df["lon"], df["lat"]))

                poly_geom = Polygon(coords_en)
                poly_ll = Polygon(coords_ll)

                line_geom = LineString(coords_en + [coords_en[0]])

                centroid_m = poly_geom.centroid
                area = poly_geom.area

                # ================== EXPORT QGIS ==================
                st.sidebar.markdown("---")
                st.sidebar.subheader("💾 Eksport Data")

                geojson_dict = {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": mapping(poly_ll),
                            "properties": {
                                "Area_sqm": round(area, 2),
                                "Stations": len(df),
                            },
                        }
                    ],
                }

                st.sidebar.download_button(
                    label="🚀 Export to QGIS (.geojson)",
                    data=json.dumps(geojson_dict),
                    file_name="survey_lot.geojson",
                    mime="application/json",
                    use_container_width=True,
                )

                st.markdown("---")

                # ================== FOLIUM MAP ==================
                if show_interactive_map:

                    google_map_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"

                    if map_provider == "Standard Map":
                        google_map_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"

                    m = folium.Map(
                        location=[df["lat"].mean(), df["lon"].mean()],
                        zoom_start=20,
                        max_zoom=22,
                        tiles=google_map_url,
                        attr="Google",
                    )

                    points_map = [[r["lat"], r["lon"]] for _, r in df.iterrows()]

                    folium.Polygon(
                        locations=points_map,
                        color=line_color,
                        weight=3,
                        fill=True,
                        fill_color=poly_color,
                        fill_opacity=poly_opacity,
                    ).add_to(m)

                    st_folium(m, width=1400, height=600)

                # ================== MATPLOTLIB ==================
                else:

                    if plot_theme == "Dark Mode":
                        bg_color, grid_color = "#121212", "#555555"

                    elif plot_theme == "Blueprint":
                        bg_color, grid_color = "#003366", "#004080"

                    else:
                        bg_color, grid_color = "#ffffff", "#aaaaaa"

                    fig, ax = plt.subplots(figsize=(10, 8))

                    fig.patch.set_facecolor(bg_color)
                    ax.set_facecolor(bg_color)

                    ax.plot(*line_geom.xy, linewidth=2, color=line_color)
                    ax.fill(*poly_geom.exterior.xy, color=poly_color, alpha=poly_opacity)

                    if show_bg_grid:

                        ax.grid(True, color=grid_color, linestyle="--", alpha=0.5)

                        ax.xaxis.set_major_locator(
                            plt.MultipleLocator(grid_interval)
                        )

                        ax.yaxis.set_major_locator(
                            plt.MultipleLocator(grid_interval)
                        )

                    if show_luas_label:

                        ax.text(
                            centroid_m.x,
                            centroid_m.y,
                            f"{area:.2f} m²",
                            fontsize=label_size_luas,
                            fontweight="bold",
                            color="darkgreen",
                            ha="center",
                        )

                    ax.set_aspect("equal")

                    st.pyplot(fig)

            else:
                st.error("❌ Kolum STN, E, N tak jumpa dalam CSV!")

        except Exception as e:
            st.error(f"❌ Ada ralat: {e}")
