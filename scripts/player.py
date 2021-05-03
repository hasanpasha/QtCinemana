
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal

class Player(QObject):
    finished = pyqtSignal()

    def __init__(self, video, subtitle, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        # self.video = queue
        # self.subtitle = subtitle

        self.playLineArgs = ['mpv']

        if video != None:
            video = video.replace("\\", '')
            self.playLineArgs.append(video)

        if subtitle != None:
            print(":: Subtitle added")
            sub = subtitle.replace("\\", '')
            self.playLineArgs.append(f'--sub-file={sub}')

        # if len(playLineArgs) > 1:

    def play(self):
        self.active = True

        if len(self.playLineArgs) > 1:
            player = subprocess.Popen(self.playLineArgs)

            print('$ ' + ' '.join(self.playLineArgs))
            while self.active:
                if player.poll() == None:
                    pass
                else:
                    break
            
            player.terminate()
            # print(player.poll())

            self.finished.emit()
