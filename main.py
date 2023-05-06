from PyQt6.QtWidgets import QApplication
from views import UI_Window
from models import Camera
from handtracking import HandTracker


if __name__ == '__main__':

    camera = Camera(0)
    hand_tracker = HandTracker()

    app = QApplication([])
    start_window = UI_Window(camera, hand_tracker)
    start_window.show()
    app.exit(app.exec())