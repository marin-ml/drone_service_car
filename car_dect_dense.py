
import numpy as np
import cv2
from imutils.object_detection import non_max_suppression


class GunnarDetection():

    def __init__(self, run_mode=0):
        self.flow0 = None
        self.flow1 = None
        self.old_gray = None
        self.run_mode = run_mode

    def opt_flow_GUNNAR(self, frame):

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Calculate the offset with magnitude and angle
        self.flow2 = self.flow1
        self.flow1 = self.flow0
        if self.old_gray is not None:
            self.flow0 = cv2.calcOpticalFlowFarneback(self.old_gray, frame_gray, None, 0.3, 5, 15, 3, 5, 5, 0)

        self.old_gray = frame_gray.copy()

        if self.flow1 is not None and self.flow2 is not None:
            flow = (self.flow0 + self.flow1 + self.flow2)/3
        else:
            flow = self.flow0

        if self.flow0 is None:
            return None

        if self.run_mode == 0:
            flow_all = np.square(flow[..., 0]) + np.square(flow[..., 1])
            flow_all *= 20
        elif self.run_mode == 1:
            flow_all = np.sqrt(np.square(flow[..., 0]) + np.square(flow[..., 1]))
            flow_all = cv2.normalize(flow_all, None, 0, 255, cv2.NORM_MINMAX)

        flow_all = flow_all.astype('uint8')

        mask3 = cv2.threshold(flow_all, 150, 255, cv2.THRESH_BINARY)[1]
        mask = cv2.dilate(mask3, np.ones((10, 10), np.uint8), iterations=1)
        im2, contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rectangle = []
        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            if frame.shape[0] / 2 > h > 10 and frame.shape[1] / 2 > w > 10:
                rectangle.append([x, y, x + w, y + h])

        rectangle = np.array(rectangle)
        pick = non_max_suppression(rectangle, probs=None, overlapThresh=0.1)

        return pick

    def calc_mask(self, frame):

        # array of magnitude and angle at each pixels of frame
        if self.flow0 is None:
            return None

        magnitude, angle = cv2.cartToPolar(self.flow0[..., 0], self.flow0[..., 1])
        hsv = np.zeros(frame.shape)
        hsv[..., 1] = 255
        hsv[..., 0] = angle * 180 / np.pi / 2
        hsv[..., 2] = magnitude * 20

        hsv = hsv.astype('uint8')
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        rgb = rgb.astype('uint8')

        return rgb


if __name__ == '__main__':

    class_gunnar = GunnarDetection(1)
    cam = cv2.VideoCapture("Sample_video/sample15.mp4")

    while True:
        ret, frame = cam.read()
        frame = cv2.resize(frame, (720, 576))

        pick = class_gunnar.opt_flow_GUNNAR(frame)

        if pick is not None:
            for rect in pick:
                frame = cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (255, 0, 0), 2)

        cv2.imshow("Movement Indicator", frame)

        mask = class_gunnar.calc_mask(frame)
        if mask is not None:
            cv2.imshow("mask", mask)

        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyAllWindows()
            break
