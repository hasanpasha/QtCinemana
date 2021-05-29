
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal

class Player(QObject):
    finished = pyqtSignal()

    def __init__(self, video, subtitle):
        QObject.__init__(self)
        self.playLineArgs = ['mpv']

        if video != None:
            video = video.replace("\\", '')
            self.playLineArgs.append(video)

        if subtitle != None:
            print(":: Subtitle added")
            sub = subtitle.replace("\\", '')
            self.playLineArgs.append(f'--sub-file={sub}')

    def play(self):
        self.active = True

        if len(self.playLineArgs) > 1:
            playerProcess = subprocess.Popen(self.playLineArgs)

            print('$ ' + ' '.join(self.playLineArgs))
            while self.active:
                if playerProcess.poll() != None:
                    break

            playerProcess.terminate()

            self.finished.emit()
