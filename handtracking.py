import mediapipe as mp
import numpy as np
import cv2

CONTROLS_IDS = [4, 8, 12, 16, 20]
CONTROLS_ALIASES = ['SWITCH', 'C1', 'C2', 'C3', 'C4']


class HandTracker:
    def __init__(self):
        self.calibrated_low = False
        self.calibrated_high = False
        self.positions = {'low': [], 'high': []}
        self.positions_xs = {'low': [], 'high': []}

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands()


    def _get_landmarks(self, frame):
        mp_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image.flags.writeable = False
        results = self.hands.process(mp_image)
        mp_image.flags.writeable = True

        if results.multi_hand_landmarks is not None:
            return results.multi_hand_landmarks[0]

    def calibrate(self, frame, low=True):
        mhl = self._get_landmarks(frame)
        if not mhl:
            return False
        landmarks = mhl.landmark
        self.positions[('low' if low else 'high')] = [landmarks[i].y for i in CONTROLS_IDS]
        self.positions_xs[('low' if low else 'high')] = [landmarks[i].x for i in CONTROLS_IDS]
        self.calibrated_low = True
        self.__setattr__(('calibrated_low' if low else 'calibrated_high'), True)
        return True

    def get_finger_positions(self, frame):
        if  not (self.calibrated_high and self.calibrated_low):
            return [-1, -1, -1, -1, -1]
        
        landmarks = self._get_landmarks(frame)
        if not landmarks:
            return [-1, -1, -1, -1, -1]
        
        lm = landmarks.landmark
        positions = [np.clip((lm[i].y - self.positions['low'][j]) / (self.positions['high'][j] - self.positions['low'][j]), 0, 1) for i, j in zip(CONTROLS_IDS, range(5))] 
        return positions
    
    def recalibrate(self):
        self.calibrated_high = self.calibrated_low = False

    def draw_calibrated_positions(self, frame):
        if self.calibrated_low:
            for i in range(5):
                wx = int(np.clip(0, 1, self.positions_xs["low"][i]) * 640)
                wy = int(np.clip(0, 1, self.positions["low"][i]) * 480)
                frame = cv2.circle(frame, (wx, wy), 5, (255, 0, 0), 5)
        if self.calibrated_high:
            for i in range(5):
                wx = int(np.clip(0, 1, self.positions_xs["high"][i]) * 640)
                wy = int(np.clip(0, 1, self.positions["high"][i]) * 480)
                frame = cv2.circle(frame, (wx, wy), 5, (0, 0, 255), 5)

        return frame




    
