from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from widgets.video_player.widget import MyVideoPlayer
import os


class RootWidget(FloatLayout):

    def on_btn_start(self):
        self.ids.video_player.path = video_path
        self.ids.video_player.on_start()

    def on_btn_stop(self):
        self.ids.video_player.on_stop()


class ScreenApp(App):

    def build(self):
        screen = Builder.load_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screen.kv'))
        return screen

if __name__ == '__main__':

    video_path = '0'
    # video_path = '../sample1.mp4'
    # video_path = 'rtsp://admin:admin@192.168.2.188:554/cam/realmonitor?channel=1&subtype=0'
    # video_path = '../image2.jpg'

    ScreenApp().run()
