
import cv2
import sys


def display(cam_setting):

    # ---------------------------- Camera Initiation Setting -----------------------------
    cap = cv2.VideoCapture(cam_setting)
    img_resize = cv2.imread('background.jpg')
    # ------------------------------- Display Camera Loop ---------------------------------
    while True:
        ret, image = cap.read()

        if image is not None:
            img_height, img_width = image.shape[:2]
            if img_width > 720:
                img_resize = cv2.resize(image, (720, int(img_height*720/img_width)), interpolation=cv2.INTER_AREA)
            else:
                img_resize = image

        cv2.imshow("Camera View", img_resize)

        k = cv2.waitKey(30)
        if k == 27:
            break

    # --------------------------------- Camera close setting -------------------------------
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    camera_setting = 0
    # camera_setting = 'sample3.mp4'
    # camera_setting = 'rtsp://admin:admin@192.168.2.188:554/cam/realmonitor?channel=1&subtype=0'
    # camera_setting = 'image2.jpg'

    display(camera_setting)
