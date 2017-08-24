
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from car_dect_knn import MoveDetection


class BestApp(App):

    screen_names = ListProperty([])
    screens = {}  # Dict of all screens

    title = StringProperty()
    btn_start_text = StringProperty()
    btn_record_text = StringProperty()
    txt_cam_setting = StringProperty()

    def __init__(self, **kwargs):
        self.run_mode = True
        self.record_mode = True
        self.event_take_video = None

        self.title = 'Drone Service'
        self.btn_start_text = 'Pause'
        self.btn_record_text = 'Record'

        self.carCascade = cv2.CascadeClassifier('models/cars1.xml')

        self.class_yolo = MoveDetection()

        self.fps = 30
        self.cam_ind = 0
        self.pro_ind = 0
        self.str_src = ['Web Camera',
                        'IP Camera',
                        'Video',
                        'Image']
        self.cam_src = ['0',
                        'rtsp://admin:admin@192.168.2.188:554/cam/realmonitor?channel=1&subtype=0',
                        'Sample_video/sample1.mp4',
                        'sample_Image/image2.jpg']

        self.cam_setting = self.cam_src[self.cam_ind]

        self._init_cv()
        self.on_resume()
        super(BestApp, self).__init__(**kwargs)

    # --------------------------- Main Menu Event -----------------------------
    def on_btn_start(self):
        if self.run_mode:
            self.btn_start_text = 'Resume'
            self.on_stop()
        else:
            self.btn_start_text = 'Pause'
            self.on_resume()

        self.run_mode = not self.run_mode

    def on_btn_record(self):
        if self.record_mode:
            self.btn_record_text = 'Stop'
        else:
            self.btn_record_text = 'Record'

        self.record_mode = not self.record_mode

    def go_setting(self):
        self.txt_cam_setting = self.cam_setting
        self.title = 'Setting'
        self.go_screen('dlg_setting', 'left')

    def on_exit(self):
        self.on_close()
        exit(0)

    # ---------------------- Camera Setting dialog Event ------------------------
    def on_sel_cam(self, cam_sel):
        self.cam_ind = cam_sel
        self.txt_cam_setting = self.cam_src[cam_sel]

    def on_sel_pro(self, pro_sel):
        self.pro_ind = pro_sel

    def on_cam_set(self, cam_setting):
        self.cam_src[self.cam_ind] = cam_setting
        self.cam_setting = cam_setting
        self._init_cv()
        self.on_resume()
        self.title = 'Camera View'
        self.go_screen('dlg_menu', 'right')

    def on_return(self):
        self.title = 'Camera View'
        self.go_screen('dlg_menu', 'right')

    # ------------------------ Image Processing -------------------------------
    def _init_cv(self):
        if self.cam_setting == '0':
            self.capture = cv2.VideoCapture(0)
        else:
            self.capture = cv2.VideoCapture(self.cam_setting)
        if not self.capture.isOpened():
            print('Failed to get source of CV')
        else:
            self.frameWidth = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frameHeight = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # self.fps = self.capture.get(cv2.CV_CAP_PROP_FPS)

    def on_resume(self):
        if self.event_take_video is None:
            self.event_take_video = Clock.schedule_interval(self.get_frame, 1.0 / self.fps)
        elif not self.event_take_video.is_triggered:
            self.event_take_video()

    def on_stop(self):
        if self.event_take_video is not None and self.event_take_video.is_triggered:
            self.event_take_video.cancel()

    def get_frame(self, *args):
        ret, frame = self.capture.read()

        if ret:
            frame = cv2.resize(frame, (720, 576))

            if self.pro_ind == 1:
                cars = self.carCascade.detectMultiScale(
                    frame,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(20, 20),
                    flags=2)

                for (x, y, w, h) in cars:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            elif self.pro_ind == 2:
                _, cars = self.class_yolo.detect_cars(frame)

                for (x1, y1, x2, y2) in cars:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            self.frame_to_buf(frame=frame)
        else:
            self.root.ids.img_video.source = 'logo/Background.jpg'
            self.event_take_video.cancel()
            Clock.unschedule(self.event_take_video)
            self.event_take_video = None

    def frame_to_buf(self, frame):
        frame = cv2.resize(frame, (self.frameWidth, self.frameHeight))
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        self.root.ids.img_video.texture = Texture.create(size=(self.frameWidth, self.frameHeight))
        self.root.ids.img_video.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

    def on_close(self):
        self.capture.release()

    def build(self):
        self.load_screen()
        self.go_screen('dlg_menu', 'right')

    def go_screen(self, dest_screen, direction):
        sm = self.root.ids.sm
        sm.switch_to(self.screens[dest_screen], direction=direction)

    def load_screen(self):
        self.screen_names = ['dlg_menu', 'dlg_setting']
        for i in range(2):
            screen = Builder.load_file(self.screen_names[i] + '.kv')
            self.screens[self.screen_names[i]] = screen
        return True

if __name__ == '__main__':
    Config.set('graphics', 'width', '1000')
    Config.set('graphics', 'height', '700')
    Config.set('graphics', 'resizable', 0)
    Config.set('kivy', 'window_icon', 'logo/favicon.ico')
    BestApp().run()
