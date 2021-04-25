
import subprocess

def mpvPlayer(video, sub):
    playLineArgs = ['mpv']

    video = video.replace("\\", '')
    playLineArgs.append(video)

    sub = sub.replace("\\", '')
    playLineArgs.append(f'--sub-file={sub}')


    if len(playLineArgs) > 1:
        # options = ["--use-filedir-conf"]
        
        # for i in options:
        #     playLineArgs.append(i)

        # print(playLineArgs)

        # Playing Video With Externel player
        try:
            player = subprocess.Popen(playLineArgs)
            output, error = player.communicate()

        except Exception as e:
            print(f"[ERROR]: {e}")
        else:
            player.wait()
                    
                
