from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian
import pydicom._storage_sopclass_uids
from skimage.util import img_as_ubyte
from skimage.exposure import rescale_intensity
from pydicom import dcmread


class DICOM:
    def __init__(self):
        self.file_path = ''
        self.file = ''
        self.keys = []
        self.meta = []
        self.image = []
        self.file_name = ''
        self.patient_info = []
        self.converted_image = []

    def dicom_open(self, file_path):
        self.file_path = file_path
        self.file = dcmread(self.file_path)
        self.keys = {x for x in dir(self.file) if x[0].isupper()} - {'PixelData'}
        self.meta = {x: getattr(self.file, x) for x in self.keys}
        self.image = self.file.pixel_array

        return self.image, self.meta

    def image_convert(self, image):
        self.image = image

        return img_as_ubyte(rescale_intensity(self.image, out_range=(0.0, 1.0)))

    def dicom_save(self, file_name, image, patient_info):
        self.file_name = file_name
        self.image = image
        self.patient_info = patient_info

        self.converted_image = self.image_convert(self.image)

        self.meta = Dataset()
        self.meta.MediaStorageSOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
        self.meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        self.meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

        self.file = FileDataset(None, {}, preamble=b"\0" * 128)
        self.file.file_meta = self.meta
        self.file.is_little_endian = True
        self.file.is_implicit_VR = False

        self.file.SOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
        self.file.SOPInstanceUID = self.meta.MediaStorageSOPInstanceUID

        self.file.PatientName = self.patient_info["PatientName"]
        self.file.PatientID = self.patient_info["PatientID"]
        self.file.PatientBirthDate = self.patient_info["PatientBirthDate"]
        self.file.ImageComments = self.patient_info["ImageComments"]

        self.file.Modality = "CT"
        self.file.SeriesInstanceUID = pydicom.uid.generate_uid()
        self.file.StudyInstanceUID = pydicom.uid.generate_uid()
        self.file.FrameOfReferenceUID = pydicom.uid.generate_uid()

        self.file.SamplesPerPixel = 1
        self.file.HighBit = 7
        self.file.BitsStored = 8
        self.file.BitsAllocated = 8

        self.file.ImagesInAcquisition = 1
        self.file.InstanceNumber = 1

        self.file.Rows, self.file.Columns = self.converted_image.shape
        self.file.ImageType = r"ORIGINAL\PRIMARY\AXIAL"
        self.file.PhotometricInterpretation = "MONOCHROME2"
        self.file.PixelRepresentation = 0

        pydicom.dataset.validate_file_meta(self.file.file_meta, enforce_standard=True)

        self.file.PixelData = self.converted_image.tobytes()
        self.file.save_as(self.file_name, write_like_original=False)

        return self.file_name
