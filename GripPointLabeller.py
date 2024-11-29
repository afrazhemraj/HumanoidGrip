import sys
import json
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox
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

        # QLabel to display the image
        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black; color: white;")
        self.layout.addWidget(self.image_label)

        # Button to open an image
        self.open_button = QPushButton("Open Image")
        self.open_button.clicked.connect(self.open_image)
        self.layout.addWidget(self.open_button)

        # Button to save points
        self.save_button = QPushButton("Save Points")
        self.save_button.clicked.connect(self.save_points)
        self.save_button.setEnabled(False)
        self.layout.addWidget(self.save_button)

    def open_image(self):
        # Open file dialog to select an image
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not file_path:
            return  # If no file is selected, do nothing

        try:
            # Load and display the image
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                raise ValueError("Unable to load image.")

            # Update attributes
            self.image_path = file_path
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

                # QMessageBox.information(
                #     self,
                #     "Point Recorded",
                #     f"Point {len(self.clicked_points)}: ({normalized_x:.2f}, {normalized_y:.2f})",
                # )

            if len(self.clicked_points) == 5:
                QMessageBox.information(
                    self, "Points Recorded", "All 5 points have been recorded."
                )
                self.save_button.setEnabled(True)

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

    def save_points(self):
        if not self.clicked_points or not self.image_path:
            QMessageBox.warning(self, "Error", "No points to save!")
            return

        # Prepare data to save
        data = {
            "image_path": self.image_path,
            "points": [{"x": x, "y": y} for x, y in self.clicked_points],
        }

        # Save to JSON file
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Points", "", "JSON Files (*.json)"
        )
        if not save_path:
            return  # Exit if no file is selected

        try:
            with open(save_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
            QMessageBox.information(self, "Success", f"Points saved to {save_path}")
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
