
# filename: _videos.py
# date: 2021/4/3

from ._logger import logger

from ._fetch import get_videos_data
from ._urls import URLS

def getVideos(nb):
    url = URLS.VIDEOS + str(nb)

     # Get the data
    logger.debug('get data from : {}'.format(url))
    data, info = get_videos_data(url)

    if data:
        return data, info
    
    else:
        # delete the last entry cache, so it won't return null next time
        get_videos_data.delete(url)
        return data, info
