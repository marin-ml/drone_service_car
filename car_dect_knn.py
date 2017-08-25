
import cv2
import numpy as np
from imutils.object_detection import non_max_suppression


class MoveDetection:

    def __init__(self, size_kernel=5, threshold=150, size_contour=10, overlap_threshold=0.1):
        self.back_object = cv2.createBackgroundSubtractorKNN()
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size_kernel, size_kernel))
        self.threshold = threshold
        self.CONTOUR_SIZE = size_contour
        self.OVERLAP_THRESHOLD = overlap_threshold

    def detect_cars(self, frame):

        # Getting background mask
        mask1 = self.back_object.apply(frame)
        mask2 = cv2.morphologyEx(mask1, cv2.MORPH_ELLIPSE, self.kernel)

        # Removing redundancy mask
        mask3 = cv2.threshold(mask2, self.threshold, 255, cv2.THRESH_BINARY)[1]
        mask = cv2.dilate(mask3, np.ones((20, 20), np.uint8), iterations=1)

        # Getting contours
        im2, contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Merging contours
        rectangle = []
        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            if frame.shape[0]/2 > h > self.CONTOUR_SIZE and frame.shape[1]/2 > w > self.CONTOUR_SIZE:
                rectangle.append([x, y, x + w, y + h])

        rectangle = np.array(rectangle)
        pick = non_max_suppression(rectangle, probs=None, overlapThresh=self.OVERLAP_THRESHOLD)

        return mask, pick


if __name__ == '__main__':
    class_move = MoveDetection()
    cam = cv2.VideoCapture("Sample_video/sample17.mp4")
    while True:
        ret, frame = cam.read()
        frame = cv2.resize(frame, (720, 576))

        mask, rect_list = class_move.detect_cars(frame)

        if rect_list is not None:
            for rect in rect_list:
                frame = cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (255, 0, 0))

        cv2.imshow("Movement Indicator", frame)
        cv2.imshow("mask", mask)

        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyAllWindows()
            break

