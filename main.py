import skimage.io
import streamlit as st
import numpy as np
from skimage.io import imread
import tomograph_module as tomograph
from dicom_module import DICOM


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
    dicom = DICOM()
    if input_image_upload.type == "application/octet-stream":
        with st.expander("Informacje o pacjencie"):
            image, info = dicom.dicom_open(input_image_upload)
            st.write(f"Imię i nazwisko: {str(info.get('PatientName'))}")
            st.write(f"ID: {str(info.get('PatientID'))}")
            st.write(f"Data badania: {str(info.get('PatientBirthDate'))}")
            st.write(f"Komentarz: {str(info.get('AdditionalPatientHistory'))}")
            image = normalization(image)
    else:
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

    with st.expander("Zapisz jako plik DICOM"):
        patient_name = st.text_input("Imię i nazwisko")
        patient_id = st.text_input("ID")
        patient_birthdate = st.date_input("Data badania")
        comment = st.text_area("Komentarz")
        patient_info = {
            "PatientName": patient_name,
            "PatientID": patient_id,
            "PatientBirthDate": str(patient_birthdate),
            "AdditionalPatientHistory": comment
        }
        if len(patient_name) and len(patient_id):
            file_name = f'{patient_name} {patient_id}.dcm'
        else:
            file_name = "unnamed.dcm"
        save_image = st.radio("Zapisz jako DICOM ", ["Obraz wejściowy", "Obraz wyjściowy"])
        if save_image == "Obraz wyjściowy":
            if st.button("Zapisz"):
                dicom.dicom_save(file_name, np.array(normalization(output_image[len(output_image) - 1])), patient_info)
        else:
            if st.button("Zapisz"):
                dicom.dicom_save(file_name, image, patient_info)