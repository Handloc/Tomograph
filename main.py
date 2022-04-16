import streamlit as st
import skimage.io
import numpy as np

st.set_page_config(page_title="IWM - Tomograf komputerowy")

with st.sidebar:
    scans_number = st.slider("Krok Δα układu emiter/dekoder", min_value=1, max_value=50, value=10, step=1)
    detectors_number = st.slider("Liczba detektorów dla układu emiter/dekoder", min_value=10, max_value=2000, value=500,
                                 step=10)
    spread_size = st.slider("Rozwartość/rozpiętość układu emiter/detektor", min_value=10, max_value=180, value=100,
                            step=1)

input_image = st.file_uploader("Wybierz plik", type=["dcm", "jpg", "jpeg"])