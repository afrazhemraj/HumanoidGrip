import sys
import os
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QMessageBox, QComboBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap


class ImageAnnotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Annotator")
        self.setGeometry(100, 100, 800, 600)

        # Attributes
        self.image_folder = None
        self.image_list = []
        self.current_image_index = 0
        self.annotations = {}  # Dictionary to store the annotations

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # QLabel to display the image
        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black; color: white;")
        self.layout.addWidget(self.image_label)

        # Dropdown menus for size and shape
        dropdown_layout = QHBoxLayout()
        self.size_dropdown = QComboBox()
        self.size_dropdown.addItems(["small", "medium", "large"])
        dropdown_layout.addWidget(QLabel("Size:"))
        dropdown_layout.addWidget(self.size_dropdown)

        self.shape_dropdown = QComboBox()
        self.shape_dropdown.addItems(["circular", "rectangular", "other"])
        dropdown_layout.addWidget(QLabel("Shape:"))
        dropdown_layout.addWidget(self.shape_dropdown)

        self.layout.addLayout(dropdown_layout)

        # Button to load folder
        self.load_folder_button = QPushButton("Load Image Folder")
        self.load_folder_button.clicked.connect(self.load_folder)
        self.layout.addWidget(self.load_folder_button)

        # Button to save annotations
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_annotation)
        self.save_button.setEnabled(False)
        self.layout.addWidget(self.save_button)

    # Gets the relative image file path given a global file path      
    def get_relative_path(self, file_path):
        # Normalize the path for cross-platform compatibility
        normalized_path = os.path.normpath(file_path)
    
        # Split the path into parts based on slashes
        path_parts = normalized_path.split(os.sep)
    
        # Get the last three parts
        relative_path_parts = path_parts[-2:]
    
        # Join the last three parts back into a relative path
        relative_path = os.path.join(*relative_path_parts).replace("\\", "/")
        relative_path = "/content/dataset/GripData/" + relative_path
    
        return relative_path

    def load_folder(self):
        # Open file dialog to select a folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if not folder_path:
            return

        # Get a list of image files in the folder
        self.image_list = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
        ]

        if not self.image_list:
            QMessageBox.warning(self, "Error", "No images found in the selected folder!")
            return

        self.image_folder = folder_path
        self.current_image_index = 0
        self.annotations = {}  # Reset annotations
        self.load_image()

    def load_image(self):
        if self.current_image_index >= len(self.image_list):
            QMessageBox.information(self, "Finished", "All images have been annotated!")
            self.image_label.setText("No Image Loaded")
            self.save_button.setEnabled(False)
            return

        # Load the current image
        file_path = self.image_list[self.current_image_index]
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                raise ValueError("Unable to load image.")

            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.save_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open image: {e}")

    def save_annotation(self):
        if self.current_image_index >= len(self.image_list):
            QMessageBox.warning(self, "Error", "No image to save!")
            return

        # Get the current image path and dropdown selections
        file_path = self.image_list[self.current_image_index]
        file_path = self.get_relative_path(file_path)
        size = self.size_dropdown.currentText()
        shape = self.shape_dropdown.currentText()

        # Save annotation in the dictionary
        self.annotations[file_path] = [size, shape]

        # Save to JSON file
        json_file_path = os.path.join(os.getcwd(), "testing.json")
        try:
            if os.path.exists(json_file_path):
                with open(json_file_path, "r") as json_file:
                    data = json.load(json_file)
            else:
                data = {}

            # Update data and write back to the file
            data.update(self.annotations)
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            # QMessageBox.information(self, "Success", f"Annotation saved for {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot save annotation: {e}")
            return

        # Load the next image
        self.current_image_index += 1
        self.load_image()


# Main function to run the app
def main():
    app = QApplication(sys.argv)
    annotator = ImageAnnotator()
    annotator.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
