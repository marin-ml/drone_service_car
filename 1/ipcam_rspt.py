# for ip camera capture with rstp

import cv2
import numpy as np
import json
import datetime

"""
# configure the connection to DAHUA IP camera
#-------------------------------------------------------------------------------------------#
|                                                                                           |
|    e.g. 'rtsp://admin:admin@192.10.0.1:554/cam/realmonitor?channel=1&subtype=0'           |
|                                                                                           |
|    username = 'admin'      # default                                                      |
|    password = 'admin'      # default                                                      |
|    protocol = 'rtsp://'                                                                   |
|    ip = '192.10.0.1'       # ip address of camera                                         |
|    port = '554'            # default                                                      |
|    channel = '1'           # default                                                      |
|    subtype = '0'           # 1 for main stream, 0 for sub stream                          |
|                                                                                           |
|                                                                                           |
|                                                                                           |
|                                                                                           |
|                                                                                           |
#-------------------------------------------------------------------------------------------#
"""
# url = 'rtsp://'
# url += username + ':'
# url += password + '@'
# url += ip + ':'
# url += port + '/cam/realmonitor?channel='
# url += channel + '&subtype='
# url += subtype


def get_cam_ips(json_fn):

    with open(json_fn) as json_file:
        data = json.load(json_file)
        cameras = []
        for p in data['cameras']:
            cameras.append(p)
    return cameras


def ipcam_capture(camera_list):

    new_height = 270
    new_width = 480
    screen = np.zeros((new_height * 2, new_width * 2, 3), dtype=np.uint8)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    protocol = 'rtsp://admin:admin@'
    camera_id = ':554/cam/realmonitor?channel=1&subtype=0'

    caps = []
    video_outs = []

    now = datetime.datetime.now()
    for cam in camera_list:
        url = protocol + cam["ip"] + camera_id

        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            print('camera connected with:' + url)
            caps.append(cap)

            fn_out = "{}_{}_{:02d}{:02d}{:02d}.avi".format(cam["id"], str(now.date()), now.hour, now.minute,
                                                           now.second)

            print('output_file :', fn_out)
            print('url :', url)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(fn_out, fourcc, 25, (height, width))
            video_outs.append(out)

        else:
            print('connected failed. please check its options.' + url)

    while True:

        for i in range(len(caps)):
            ret, frame = caps[i].read()

            row = int(i / 2) * new_height
            col = int((i % 2) * new_width)

            if ret:
                video_outs[i].write(frame)
                frame = cv2.resize(frame, (new_width, new_height))
                screen[row:row+new_height, col:col+new_width] = frame[:new_height, :new_width]
            else:
                print("disconnected the" + str(i) + "th camera.")
                for i in range(len(caps)):
                    caps[i].release()
                    video_outs[i].release()
                cv2.destroyAllWindows()
                return

        cv2.imshow("frames", screen)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for i in range(len(caps)):
        caps[i].release()
        video_outs[i].release()
    cv2.destroyAllWindows()

if __name__ == '__main__':

    json_fn = './cameras.json'
    cameras = get_cam_ips(json_fn)
    ipcam_capture(cameras)

