from PyQt6.QtCore import QThread, QTimer, Qt
from PyQt6.QtWidgets import QLabel, QWidget, QPushButton, QVBoxLayout, QApplication, QHBoxLayout, QMessageBox, QGridLayout, QSlider
from PyQt6.QtGui import QPixmap, QImage
import cv2

from models import Camera
from handtracking import HandTracker, CONTROLS_ALIASES
from midi_sender import MidiSender

class UI_Window(QWidget):

    def __init__(self, camera: Camera = None, hand_tracker: HandTracker = None, midi_sender: MidiSender = None):
        super().__init__()
        self.camera = camera
        self.hand_tracker = hand_tracker
        self.midi_sender = midi_sender

        self.positions = [-1, -1, -1, -1, -1]

        self.switch_activated = False

        # Create a timer.
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)

        # setup layout
        layout = self._setup_layout()

        # Set the layout
        self.setLayout(layout)
        self.setWindowTitle("First GUI with QT")
        # self.setFixedSize(900, 900)

    def start(self):
        self._hide_button(self.start_button)
        self._show_button(self.stop_button)

        self.label.setText('Opening...')
        if not self.camera.open():
            print('failure')
            msgBox = QMessageBox()
            msgBox.setText("Failed to open camera.")
            msgBox.exec()
            return
        self.timer.start(1000 // 24)

    def stop(self):
        self.timer.stop()
        self.label.clear()
        self.camera.close()

        self._hide_button(self.stop_button)
        self._show_button(self.start_button)

    def calibrate(self, low=True):
        self.hand_tracker.calibrate(self.camera.read(), low)
        if self.hand_tracker.calibrated_low and self.hand_tracker.calibrated_high:
            self._show_button(self.recalibrate_button)
            for label in self.pos_labels:
                label.setDisabled(False)

    def recalibrate(self):
        self.hand_tracker.recalibrate()
        self.recalibrate_button.setDisabled(True)
        for label in self.pos_labels:
            label.setDisabled(True)
            label.setNum(-1)

    def update_positions(self, frame):
        if self.hand_tracker.calibrated_low and self.hand_tracker.calibrated_high:
            self.positions = self.hand_tracker.get_finger_positions(frame)
            for i in range(len(self.positions)):
                self.pos_labels[i].setNum(self.positions[i])

    def nextFrameSlot(self):
        frame = self.camera.read()
        self.update_positions(frame)
        frame = self.hand_tracker.draw_calibrated_positions(frame)
        self._set_switch()
        if self.switch_activated:
            for i in range(1, 5):
                self.midi_sender.control_change(i, self.positions[i])
        frame = self._convert_frame_to_rgb(frame)
        #frame = self.camera.read_gray()
        if frame is not None:
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.label.setPixmap(pixmap)

    def _convert_frame_to_rgb(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def _setup_layout(self):
        layout = QHBoxLayout()

        camera_layout = self._create_camera_layout()
        settings_layout = self._setup_settings_layout()

        layout.addLayout(camera_layout)
        layout.addLayout(settings_layout)

        return layout

    def _create_camera_layout(self):

        camera_layout = QVBoxLayout() # TODO: perenesti

        # Add a label
        self.label = QLabel()
        self.label.setFixedSize(640, 640)

        camera_layout.addWidget(self.label)

        return camera_layout

    def _setup_settings_layout(self):
        layout = QVBoxLayout()

        # # open and close camera buttons
        camera_button_layout = self._create_open_camera_button_layout()
        layout.addLayout(camera_button_layout)

        # calibrate and recalibrate buttons
        calibrate_button_layout = self._create_calibration_buttons_layout()
        layout.addLayout(calibrate_button_layout)

        # create positions info layout
        positions_info_layout = self._create_positions_info_layout()
        layout.addLayout(positions_info_layout)

        # threshold for detecting edit mode buttons
        threshold_layout = self._create_threshold_layout()
        layout.addLayout(threshold_layout)

        # binding buttons layouts
        binding_buttons_layout = self._create_binding_buttons_layout()
        layout.addLayout(binding_buttons_layout)

        return layout

    def _create_open_camera_button_layout(self):
        # open and close camera buttons
        camera_button_layout = QHBoxLayout()

        self.start_button = QPushButton("Open camera")
        self.start_button.clicked.connect(self.start)

        self.stop_button = QPushButton("Close Camera")
        self._hide_button(self.stop_button)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.clicked.connect(self.recalibrate)

        camera_button_layout.addWidget(self.start_button)
        camera_button_layout.addWidget(self.stop_button)

        return camera_button_layout

    def _create_calibration_buttons_layout(self):
        calibrate_button_layout = QHBoxLayout()

        self.calibrate_low_button = QPushButton("Calibrate rest position")
        self.calibrate_low_button.clicked.connect(lambda: self.calibrate(low=True))
        self.calibrate_high_button = QPushButton("Calibrate up position")
        self.calibrate_high_button.clicked.connect(lambda: self.calibrate(low=False))
        self.recalibrate_button = QPushButton('Recalibrate')
        self.recalibrate_button.setDisabled(True)
        self.recalibrate_button.clicked.connect(self.recalibrate)

        calibrate_button_layout.addWidget(self.calibrate_low_button)
        calibrate_button_layout.addWidget(self.calibrate_high_button)
        calibrate_button_layout.addWidget(self.recalibrate_button)

        return calibrate_button_layout

    def _create_positions_info_layout(self):
        positions_info_layout = QGridLayout()
        positions_info_layout.setContentsMargins(0,0,0,0)
        positions_info_layout.setSpacing(0)

        self.pos_labels = []
        for i in range(5):
            label = QLabel()
            label.setText(CONTROLS_ALIASES[i])
            label_pos = QLabel()
            label_pos.setDisabled(True)
            label_pos.setNum(-1)
            self.pos_labels.append(label_pos)
            positions_info_layout.addWidget(label, 0, i)
            positions_info_layout.addWidget(label_pos, 1, i)

        positions_info_layout.setRowStretch(2,0)

        return positions_info_layout

    def _create_threshold_layout(self):
        threshold_layout = QGridLayout()
        # threshold_layout.setContentsMargins(0,0,0,0)
        # threshold_layout.setSpacing(0)

        threshold_layout.addWidget(QLabel("Activate threshold value:"), 0, 0)

        self.threshold_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setSliderPosition(60)
        self.threshold_slider.setDisabled(False)
        self.threshold_slider.setTickInterval(5)
        self.threshold_slider.valueChanged.connect(self._update_threshold_value)


        self.threshold_val = QLabel()
        self.threshold_val.setNum(0.6)

        threshold_layout.addWidget(self.threshold_val, 1, 0)
        threshold_layout.addWidget(self.threshold_slider, 1, 1)

        threshold_layout.setRowStretch(2,0)

        return threshold_layout

    def _create_binding_buttons_layout(self):
        layout = QGridLayout()
        bind_controls_label = QLabel()
        bind_controls_label.setText('Bind controls:')
        layout.addWidget(bind_controls_label, 0, 0)

        buttons = []
        for i in range(1, 5):
            button = QPushButton()
            button.setText('C' + str(i))
            buttons.append(button)
            layout.addWidget(button, 1, i-1)

        buttons[0].clicked.connect(lambda: self.midi_sender.bind_control(1))
        buttons[1].clicked.connect(lambda: self.midi_sender.bind_control(2))
        buttons[2].clicked.connect(lambda: self.midi_sender.bind_control(3))
        buttons[3].clicked.connect(lambda: self.midi_sender.bind_control(4))

        layout.setRowStretch(2,1)

        return layout

    def _update_threshold_value(self):
        self.detection_threshold = self.threshold_slider.value() / 100
        self.threshold_val.setNum(self.threshold_slider.value() / 100)

    def _set_switch(self):
        if self.positions[0] >= self.threshold_slider.value() / 100:
            self.switch_activated = True
        else:
            self.switch_activated = False

    def _hide_button(self, button):
        button.setEnabled(False)
        button.hide()

    def _show_button(self, button):
        button.setEnabled(True)
        button.show()




class MovieThread(QThread):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    def run(self):
        self.camera.acquire_movie(200)

if __name__ == '__main__':
    app = QApplication([])
    window = UI_Window()
    window.show()