

from ring import lru

from urllib.request import urlopen

@lru(maxsize=150)
def get_thumb_image(url):
    try:
        data = urlopen(url).read()
    except Exception as e:
        print(e)
    else:
        return data


@lru(maxsize=25)
def get_poster_image(url):
    try:
        data = urlopen(url).read()
    except Exception as e:
        print(e)
    else:
        return data
