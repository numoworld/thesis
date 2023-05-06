import cv2 as cv
import mediapipe as mp
import numpy as np

url = 'http://192.168.0.110:4747/video'
mp_hands = mp.solutions.hands   
mp_draw = mp.solutions.drawing_utils

CONTROLS_ALIASES = ['SWITCH', 'C1', 'C2', 'C3', 'C4']
CONTROLS_IDS = [4, 8, 12, 16, 20]
DEBUG = True


def calibrate(landmark):
    positions = [landmark[i].y for i in CONTROLS_IDS]
    if DEBUG:
        print('calibrated')
        print(positions)
    return positions

def get_hand_landmarks(image, hands):
    mp_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    mp_image.flags.writeable = False
    results = hands.process(mp_image)
    mp_image.flags.writeable = True

    if results.multi_hand_landmarks is not None:
        return results.multi_hand_landmarks[0]

def print_positions(frame, positions):
    positions = [str(num)[:3] for num in positions]
    pos_str = ' '.join(positions)
    frame = cv.putText(frame, pos_str, (90, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv.LINE_AA)
    return frame


def main():
    cap = cv.VideoCapture(url
        )
    calibrated = False
    calibrated_low = False
    hands = mp_hands.Hands()
    calibrated_text = 'NOT CALIBRATED'
    calibrated_text_color = (0, 0, 255)
    cpl = []
    cph = []
    while True:
        ret, frame = cap.read()

        frame = cv.flip(frame, 1)
        
        landmarks = get_hand_landmarks(frame, hands)
        if calibrated:
            if landmarks:
                lm = landmarks.landmark
                positions = [np.clip((lm[i].y - cpl[j]) / (cph[j]-cpl[j]), 0, 1) for i, j in zip(CONTROLS_IDS, range(5))] 
                frame = print_positions(frame, positions)



        frame = cv.putText(frame, calibrated_text, (30, 30), cv.FONT_HERSHEY_SIMPLEX, 1, calibrated_text_color, 2, cv.LINE_AA)

        cv.imshow('Video', frame)

        key = cv.waitKey(1)
        if key & 0xFF == ord('c'):
            print('ok')
            if landmarks:
                if not calibrated_low:
                    cpl = calibrate(landmarks.landmark)
                    calibrated_text = 'CALIBRATE HIGH'
                    calibrated_text_color = (0, 255, 255)
                    calibrated_low = True
                else:
                    cph = calibrate(landmarks.landmark)
                    calibrated = True
                    calibrated_text = 'CALIBRATED'
                    calibrated_text_color = (0, 255, 0) 
        elif key & 0xFF == ord('r'):
            calibrated_text = 'RECALIBRATE'
            calibrated_text_color = (0, 0, 255)
            calibrated = False
            calibrated_low = False

            
        elif key & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()