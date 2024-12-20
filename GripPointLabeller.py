import sys
import os
import json
# GUI Components
from PyQt5.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QMessageBox, QComboBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint



class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grip Point Data Labeller")
        self.setGeometry(100, 100, 800, 600)

        # Attributes to track image and points
        self.image_path = None
        self.clicked_points = []  # List to store clicked points
        self.displayed_pixmap = None  # QPixmap displayed on the QLabel

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # IMAGE
        # QLabel to display the user uploaded image
        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black; color: white;")
        self.layout.addWidget(self.image_label)

        # FEATURE VALUES (Size and Shape)
        dropdown_layout = QHBoxLayout()
        # Dropdown menu for size 
        self.size_dropdown = QComboBox()
        self.size_dropdown.addItems(["small", "medium", "large"])
        self.size_dropdown.setToolTip("Select the size of the object")
        dropdown_layout.addWidget(QLabel("Size:"))
        dropdown_layout.addWidget(self.size_dropdown)

        # Dropdown menu for shape 
        self.shape_dropdown = QComboBox()
        self.shape_dropdown.addItems(["circular", "rectangular", "other"])
        self.shape_dropdown.setToolTip("Select the shape of the object")
        dropdown_layout.addWidget(QLabel("Shape:"))
        dropdown_layout.addWidget(self.shape_dropdown)

        self.layout.addLayout(dropdown_layout)

        # Button to upload an image
        self.open_button = QPushButton("Open Image")
        self.open_button.clicked.connect(self.open_image)
        self.layout.addWidget(self.open_button)
        # Button to save the annotated points
        self.save_button = QPushButton("Save Points")
        self.save_button.clicked.connect(self.save_points)
        self.save_button.setEnabled(False)
        self.layout.addWidget(self.save_button)

    # Gets the relative image file path given a global file path      
    def get_relative_path(self, file_path):
        # Normalize the path for cross-platform compatibility
        normalized_path = os.path.normpath(file_path)
    
        # Split the path into parts based on slashes
        path_parts = normalized_path.split(os.sep)
    
        # Get the last three parts
        relative_path_parts = path_parts[-3:]
    
        # Join the last three parts back into a relative path
        relative_path = os.path.join(*relative_path_parts).replace("\\", "/")
    
        return relative_path
    
    # Callback function for the upload image GUI button
    def open_image(self):
        # Open file dialog to select an image
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not file_path:
            return

        try:
            # Load and display the image
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                raise ValueError("Unable to load image.")

            # Update attributes
            self.image_path = self.get_relative_path(file_path)
            self.clicked_points = []  # Reset points
            self.save_button.setEnabled(False)

            # Display the image
            self.displayed_pixmap = pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(self.displayed_pixmap)
            self.image_label.mousePressEvent = self.record_click  # Bind mouse click event
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open image: {e}")

    # Mouse click event to record points
    def record_click(self, event):
        if len(self.clicked_points) < 5:
            # Calculate the displayed image bounds within the QLabel
            pixmap_width = self.displayed_pixmap.width()
            pixmap_height = self.displayed_pixmap.height()
            label_width = self.image_label.width()
            label_height = self.image_label.height()

            # Calculate offsets for centering
            x_offset = (label_width - pixmap_width) / 2
            y_offset = (label_height - pixmap_height) / 2

            # Map the click to image coordinates (check bounds first)
            x = event.pos().x() - x_offset
            y = event.pos().y() - y_offset

            # Ensure click is within image bounds
            if 0 <= x <= pixmap_width and 0 <= y <= pixmap_height:
                # Normalize coordinates relative to image dimensions
                normalized_x = x / pixmap_width
                normalized_y = y / pixmap_height

                self.clicked_points.append((normalized_x, normalized_y))

                # Draw a circle on the displayed image
                self.draw_circle(x, y)

            if len(self.clicked_points) == 5:
                QMessageBox.information(
                    self, "Points Recorded", "All 5 points have been recorded."
                )
                self.save_button.setEnabled(True)
    
    # Overlay a small red circle where the user has annotated a grip point
    def draw_circle(self, x, y):
        # Create a painter to draw on the image
        pixmap_copy = self.displayed_pixmap.copy()  # Work on a copy to preserve the original
        painter = QPainter(pixmap_copy)
        pen = QPen(Qt.red)
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw a circle at the given coordinates
        radius = 4
        painter.drawEllipse(QPoint(x, y), radius, radius)
        painter.end()

        # Update the QLabel with the new pixmap
        self.image_label.setPixmap(pixmap_copy)
        self.displayed_pixmap = pixmap_copy  # Update the displayed pixmap

    # Append the 5 points and feature labels to annotations.json 
    def save_points(self):
        if not self.clicked_points or not self.image_path:
            QMessageBox.warning(self, "Error", "No points to save!")
            return
        
        # Get the dropdown selections
        size = self.size_dropdown.currentText()
        shape = self.shape_dropdown.currentText()

        # Prepare data to append
        new_data = {
            "image_path": self.image_path,
            "points": [{"x": x, "y": y} for x, y in self.clicked_points],
            "size": size,
            "shape": shape,
        }

        # Define the JSON file name
        json_file_path = os.path.join(os.getcwd(), "annotations.json")

        try:
            # Check if the JSON file already exists
            if os.path.exists(json_file_path):
                # Load existing data
                with open(json_file_path, "r") as json_file:
                    data = json.load(json_file)
                # Ensure it's a list
                if not isinstance(data, list):
                    QMessageBox.warning(self, "Error", "Existing file format is invalid!")
                    return
            else:
                # If the file doesn't exist, start with an empty list
                data = []

            # Append new data to the list
            data.append(new_data)

            # Save updated data back to the file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
            QMessageBox.information(self, "Success", f"Points appended to {json_file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot save points: {e}")



# Main function to run the app
def main():
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
