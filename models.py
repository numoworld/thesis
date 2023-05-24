import cv2

class Camera:

    def __init__(self, camera):
        self.camera = camera

    def open(self, width=640, height=480, fps=24):
        self.vc = cv2.VideoCapture(self.camera)

        self.width = width
        self.height = height
        self.fps = fps
        self.vc.set(5, fps)  #set FPS
        self.vc.set(3, width)   # set width
        self.vc.set(4, height)  # set height

        return self.vc.isOpened()

    def close(self):
        if self.vc:
            self.vc.release()

    def read(self):
        rval, frame = self.vc.read()
        if frame is not None:
            frame = cv2.flip(frame, 1)
            return frame
