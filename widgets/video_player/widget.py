import os
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.clock import Clock
import cv2
from kivy.graphics.texture import Texture


class MyVideoPlayer(Image):

    path = StringProperty()

    def __init__(self, **kwargs):

        cur_dir = os.path.dirname(os.path.realpath(__file__))
        self.bad_camera_png = os.path.join(cur_dir, 'bad_camera.png')
        self.source = self.bad_camera_png
        self.event_take_video = None
        self.fps = 30
        super(MyVideoPlayer, self).__init__(**kwargs)

    # called when the source property is upgraded
    def on_path(self, *args):
        if self.path == '0':
            self.cam_mode = 0
        else:
            self.cam_mode = self.path

        self._init_cv()

    def _init_cv(self):
        self.capture = cv2.VideoCapture(self.cam_mode)
        if not self.capture.isOpened():
            print('Failed to get source of CV')
        else:
            # self.capture = cv2.VideoCapture(self.path)
            self.frameWidth = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frameHeight = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # self.fps = self.capture.get(cv2.CV_CAP_PROP_FPS)

    def on_start(self):
        if self.event_take_video is None:
            # Call `self.take_video` 30 times per sec
            self.event_take_video = Clock.schedule_interval(self.get_frame, 1.0 / self.fps)
        elif not self.event_take_video.is_triggered:
            self.event_take_video()

    def on_stop(self):
        if self.event_take_video is not None and self.event_take_video.is_triggered:
            self.event_take_video.cancel()

    def get_frame(self, *args):
        """        Capture video frame and update image widget        """
        ret, frame = self.capture.read()
        if ret:
            self.frame_to_buf(frame=frame)
        else:
            self.source = self.bad_camera_png
            self.event_take_video.cancel()
            Clock.unschedule(self.event_take_video)
            self.event_take_video = None

    def frame_to_buf(self, frame):
        frame = cv2.resize(frame, (self.frameWidth, self.frameHeight))
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        self.texture = Texture.create(size=(self.frameWidth, self.frameHeight))
        self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

    def on_close(self):
        self.capture.release()
