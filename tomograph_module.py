import numpy as np
import skimage.draw as draw
import math
import copy


class CTScanner:
    def __init__(self, input_image, scans_number, detectors_number, spread_size):
        self.image = input_image
        self.scans_number = scans_number
        self.detectors_number = detectors_number
        self.spread_size = spread_size
        self.sinogram_img = []
        self.side = 0
        self.ax = 0
        self.ay = 0
        self.pad_size = 200
        self.file = ''
        self.side_length = 0
        self.circle_radius = 0
        self.circle_center = 0
        self.scans_angles = 0
        self.empty_image = 0
        self.number_of_scans_images = 0
        self.scan_process_index = 0
        self.scan_images = []
        self.scan_process_index_list = ''
        self.detectors = ''
        self.emitters = ''
        self.sinogram_row = ''
        self.vector = 0
        self.pad_width = 0
        self.axis = 0
        self.kwargs = 0
        self.padding = 0
        self.angles = 0
        self.angle_shift = 0
        self.angle_range = 0
        self.all_angles = 0
        self.points = 0
        self.circle_x = 0
        self.circle_y = 0
        self.x = 0
        self.y = 0
        self.line = []
        self.sinogram = ''
        self.output_image = ''

    def main_process(self):
        self.side = max(self.image.shape[0:2])
        self.file = np.zeros((self.side, self.side), np.float64)
        self.ax = (self.side - self.image.shape[1]) // 2  # Centering coords
        self.ay = (self.side - self.image.shape[0]) // 2  # Centering coords

        # Centering image
        self.file[self.ay:self.image.shape[0] + self.ay, self.ax:self.ax + self.image.shape[1]] = self.image
        self.side_length = self.file.shape[0]

        if self.side_length > 900:
            self.file = np.pad(self.file, self.pad_size, self.padding_width, padder=0)
            self.side_length = self.file.shape[0]

        self.circle_radius = self.file.shape[0] // 2
        self.circle_center = np.floor(np.array(self.file.shape) / 2).astype(int)

        self.scans_angles = np.linspace(0, 180, self.scans_number).astype(int)
        self.empty_image = np.zeros((self.side_length, self.side_length))

        self.number_of_scans_images = self.scans_number // 5
        if self.number_of_scans_images >= 10:
            self.number_of_scans_images = self.scans_number // 9

        self.scan_process_index_list = np.linspace(0, self.scans_number, self.number_of_scans_images).astype(int)

        for scan_iteration in range(self.scans_number):
            self.detectors = self.detector_points(self.scans_angles[scan_iteration], self.spread_size,
                                                  self.detectors_number, self.circle_radius, self.circle_center)
            self.emitters = self.emitter_points(self.scans_angles[scan_iteration], self.spread_size,
                                                self.detectors_number, self.circle_radius, self.circle_center)
            self.sinogram_row = self.tomograph_reconstruction(self.detectors, self.emitters, self.file,
                                                              self.empty_image)
            self.sinogram_img.append(self.sinogram_row)

            if scan_iteration == self.scan_process_index_list[self.scan_process_index]:
                self.scan_images.append(copy.copy(self.empty_image))

                self.scan_process_index += 1

        self.scan_images.append(copy.copy(self.empty_image))

        return self.scan_images, self.sinogram_img

    def padding_width(self, vector, pad_width, axis, kwargs):
        self.vector = vector
        self.pad_width = pad_width
        self.axis = axis
        self.kwargs = kwargs

        self.padding = self.kwargs.get('padder', 10)
        self.vector[:self.pad_width[0]] = self.padding
        self.vector[-self.pad_width[1]:] = self.padding

    def detector_points(self, angles, spread_size, detectors_number, circle_radius, circle_center):
        self.angles = angles
        self.spread_size = spread_size
        self.detectors_number = detectors_number
        self.circle_radius = circle_radius
        self.circle_center = circle_center
        self.angle_shift = math.radians(self.angles - self.spread_size / 2)
        self.angle_range = math.radians(self.spread_size)
        self.all_angles = np.linspace(0, self.angle_range, self.detectors_number) + self.angle_shift
        self.points = self.angle_points(self.all_angles, self.circle_center, self.circle_radius)

        return self.points

    def emitter_points(self, angles, spread_size, detectors_number, circle_radius, circle_center):
        self.angles = angles
        self.spread_size = spread_size
        self.detectors_number = detectors_number
        self.circle_radius = circle_radius
        self.circle_center = circle_center
        self.angle_shift = math.radians(self.angles - self.spread_size / 2 + 180)
        self.angle_range = math.radians(self.spread_size)
        self.all_angles = np.linspace(0, self.angle_range, self.detectors_number) + self.angle_shift
        self.points = self.angle_points(self.all_angles, self.circle_center, self.circle_radius)

        return self.points

    def angle_points(self, angles, circle_center, circle_radius):
        self.angles = angles
        self.circle_center = circle_center
        self.circle_radius = circle_radius
        self.circle_x, self.circle_y = self.circle_center
        self.x = self.circle_radius * np.cos(self.angles) - self.circle_x
        self.y = self.circle_radius * np.sin(self.angles) - self.circle_y
        self.points = np.array(list(zip(self.x, self.y)))

        return self.points

    def tomograph_reconstruction(self, detectors, emitters, file, output_image):
        self.detectors = detectors
        self.emitters = emitters
        self.file = file
        self.output_image = output_image
        self.sinogram_row = []

        for i in range(len(self.detectors)):
            self.line = draw.line_nd(self.emitters[len(self.emitters) - 1 - i], self.detectors[i])
            self.sinogram = np.average(self.file[self.line])
            self.sinogram_row.append(self.sinogram)
            self.output_image[self.line] += self.sinogram

        return self.sinogram_row
