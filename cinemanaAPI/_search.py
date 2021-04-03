
# filename: _search.py
# date: 2021/4/3 Sat

# Allowed kwargs
alakwargs = [
    'level',
    'videoTitle',
    'year',
    'type',
    'page',
    'star',
]

from ._urls import URLS
from ._fetch import get_search_data
from ._logger import logger

# to encode the params
from urllib.parse import urlencode

def search(**infos):
    for key in infos.keys():
        toRemove = []
        if key not in alakwargs:
            toRemove.append(key)
    for key in toRemove:
        infos.pop(key)

    # Prepare the url
    url = URLS.SEARCH + urlencode(infos)
    # print(url)

    # Get the data
    logger.debug('get data from : {}'.format(url))
    data, info = get_search_data(url)

    if data:
        return data[0], info
    
    else:
        # delete the last entry cache, so it won't return null next time
        get_search_data.delete(url)
        return data, info
