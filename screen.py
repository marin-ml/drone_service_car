from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
import os
import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture


class RootWidget(FloatLayout):

    def __init__(self, **kwargs):
        self.run_mode = True
        self.event_take_video = None
        self.fps = 30
        self.cam_mode = video_path
        self._init_cv()
        self.on_resume()
        super(RootWidget, self).__init__(**kwargs)

    def on_btn_start(self):
        if self.run_mode:
            self.btn_start.text = 'Resume'
            self.on_stop()
        else:
            self.btn_start.text = 'Pause'
            self.on_resume()

        self.run_mode = not self.run_mode

    def on_btn_record(self):
        if self.btn_record.text == 'Record':
            self.btn_record.text = 'Stop'
        else:
            self.btn_record.text = 'Record'

    def _init_cv(self):
        self.capture = cv2.VideoCapture(self.cam_mode)
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
            self.frame_to_buf(frame=frame)
        else:
            self.img_video.source = 'Sample_Image/Background.jpg'
            self.event_take_video.cancel()
            Clock.unschedule(self.event_take_video)
            self.event_take_video = None

    def frame_to_buf(self, frame):
        frame = cv2.resize(frame, (self.frameWidth, self.frameHeight))
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        self.img_video.texture = Texture.create(size=(self.frameWidth, self.frameHeight))
        self.img_video.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

    def on_close(self):
        self.capture.release()


class ScreenApp(App):

    def build(self):
        screen = Builder.load_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screen.kv'))
        return screen


if __name__ == '__main__':

    # video_path = '0'
    video_path = 'Sample_video/sample1.mp4'
    # video_path = 'rtsp://admin:admin@192.168.2.188:554/cam/realmonitor?channel=1&subtype=0'
    # video_path = 'sample_Image/image2.jpg'

    ScreenApp().run()
