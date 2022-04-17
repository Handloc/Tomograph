import streamlit as st
import numpy as np
from skimage.io import imread
import tomograph_module as tomograph

st.set_page_config(page_title="IWM - Tomograf komputerowy")

with st.sidebar:
    scans_number = st.slider("Krok Δα układu emiter/dekoder", min_value=10, max_value=360, value=100, step=1)
    detectors_number = st.slider("Liczba detektorów dla układu emiter/dekoder", min_value=10, max_value=2000, value=500,
                                 step=10)
    spread_size = st.slider("Rozwartość/rozpiętość układu emiter/detektor", min_value=10, max_value=180, value=100,
                            step=1)

input_image_upload = st.file_uploader("Wybierz plik", type=["dcm", "jpg", "jpeg"])


def normalization(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))


if input_image_upload:
    image = imread(input_image_upload, True)
    st.image(image, "Oryginalny obraz")
    ct_scanner = tomograph.CTScanner(image, scans_number, detectors_number, spread_size)
    output_image, sinogram = ct_scanner.main_process()
    st.write("\n\n\n")
    show_sinogram_iteration = st.checkbox("Pokaż iteracje sinogramu")
    if show_sinogram_iteration:
        sinogram_image_iteration = st.slider("", min_value=1, max_value=9,
                                             value=9, step=1)
        st.image(normalization(sinogram[:sinogram_image_iteration * 11]), "Sinogram", 703)
    else:
        st.image(normalization(sinogram), "Sinogram", 703)

    show_output_image_iteration = st.checkbox("Pokaż iteracje obrazku końcowego")
    if show_output_image_iteration:
        output_image_iteration = st.slider("", min_value=1, max_value=len(output_image),
                                           value=len(output_image), step=1)
        st.image(normalization(output_image[output_image_iteration - 1]), "Obraz końcowy")
    else:
        st.image(normalization(output_image[len(output_image) - 1]), "Obraz końcowy")