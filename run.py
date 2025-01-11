import sys
import pandas as pd
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QFileDialog, QWidget
from PyQt6.QtGui import QPixmap, QImage,QGuiApplication
from PyQt6.QtCore import Qt, QTimer

# Reading CSV file with pandas and giving names to each column
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# function to calculate minimum distance from all colors and get the most matching color
def get_color_name(param_red, param_green, param_blue):
    minimum = 10000
    color_name = ""
    for i in range(len(csv)):
        d = abs(param_red - int(csv.loc[i, "R"])) + abs(param_green - int(csv.loc[i, "G"])) + abs(
            param_blue - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            color_name = csv.loc[i, "color_name"]
    return color_name

# Write color info into the file after clicked
def write_file(filepath, content):
    f = open(filepath, "a")
    f.write(content + "\n")

class ColorReader (QWidget):
    # Function Render GUI
    def __init__(self):
        super().__init__()

        # Resize to half the screen and center
        screen_geo = QGuiApplication.primaryScreen().availableGeometry()
        width, height = screen_geo.width(), screen_geo.height()
        self.resize(width // 2, height // 2)
        self.move(width // 4, height // 4)

        self.setWindowTitle("Assessment 2 Color Code Reader")
        self.image = None
        self.double_clicked = False
        self.camera_active = False
        self.timer = QTimer()
        self.capture = None

        layout = QVBoxLayout()
        self.upload_button = QPushButton ("Upload Image")
        self.upload_button.clicked.connect(self.uploadImage)

        self.image_label = QLabel("No image uploaded.")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_camera_button = QPushButton("Start Camera")
        self.start_camera_button.clicked.connect(self.startCamera)
        self.stop_camera_button = QPushButton("Stop Camera")
        self.stop_camera_button.clicked.connect(self.stopCamera)
        self.stop_camera_button.setEnabled(False)

        layout.addWidget(self.upload_button)
        layout.addWidget(self.start_camera_button)
        layout.addWidget(self.stop_camera_button)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        self.overlay_info = None

    # Function Upload Image by file Path
    def uploadImage(self):
        self.image_label.clear()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select an Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.image = cv2.imread(file_path)
            self.displayImage()
            self.setMouseTracking(True)

    # Function DisplayImage after get from uploadImage
    def displayImage(self):
        if self.image is not None:
            height, width, channel = self.image.shape
            bytes_per_line = channel * width
            q_image = QImage(self.image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image.rgbSwapped())

            # Scale the pixmap to fit the label’s size, keeping aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def startCamera(self):
        self.image_label.clear()
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("Error: Unable to access camera.")
            return

        self.camera_active = True
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)
        self.start_camera_button.setEnabled(False)
        self.stop_camera_button.setEnabled(True)

    def stopCamera(self):
        self.timer.stop()
        if self.capture:
            self.capture.release()
        self.camera_active = False
        self.start_camera_button.setEnabled(True)
        self.stop_camera_button.setEnabled(False)
        self.image_label.clear()

# Function Display camera frame
    def updateFrame(self):
        ret, frame = self.capture.read()
        if ret:
            # Draw overlay if available
            if self.overlay_info:
                cv2.rectangle(frame, (20, 20), (750, 60), self.overlay_info["color"], -1)
                text = self.overlay_info["text"]
                cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
                if sum(self.overlay_info["color"]) >= 600:
                    cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

            self.image = frame
            height, width, channels = frame.shape
            bytes_per_line = channels * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image.rgbSwapped())

            # Scale the pixmap to fit the label’s size, keeping aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    # Function on Event Double Click on image
    def mouseDoubleClickEvent(self, event):
        if self.image is not None and event.button() == Qt.MouseButton.LeftButton:
            # 1) Get mouse coordinates *in the label's coordinate system*
            label_x = event.position().x()
            label_y = event.position().y()

            # 2) Get the label's current (visible) size
            label_w = self.image_label.width()
            label_h = self.image_label.height()

            # 3) Get the actual image size from self.image
            img_h, img_w, _ = self.image.shape

            # 4) Compute scale factors: how many image pixels per label pixel
            scale_x = img_w / label_w
            scale_y = img_h / label_h

            # 5) Convert label coordinates to image coordinates
            x = int(label_x * scale_x)
            y = int(label_y * scale_y)

            # 6) Check bounds (important to avoid out-of-range indexing)
            if 0 <= x < img_w and 0 <= y < img_h:
                self.blue, self.green, self.red = self.image[y, x]
                self.double_clicked = True

                # Draw and display the color info
                self.displayColorInfo()


    # Function display the color informations after mouse double clicked
    def displayColorInfo(self):
        if self.double_clicked:
            cv2.rectangle(self.image, (20, 20), (750, 60), (int(self.blue), int(self.green), int(self.red)), -1)

            text = get_color_name(self.red, self.green, self.blue) + f' R={self.red} G={self.green} B={self.blue}'
            cv2.putText(self.image, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

            if self.red + self.green + self.blue >= 600:
                cv2.putText(self.image, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

            self.overlay_info = {
                "color": (int(self.blue), int(self.green), int(self.red)),
                "text": text
            }

            write_file("./clicked_color.txt", text)
            self.displayImage()
            self.double_clicked = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorReader()
    window.show()
    sys.exit(app.exec())
