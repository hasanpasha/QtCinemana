
# filename: _search.py
# date: 2021/4/3 Sat

# Allowed kwargs
allokwargs = {
    'itemsPerPage': [range(2, 100), 30],
    'level': [[0, 1], 0],
    'videoKind': [[1, 2], 1],
    'sortParam': [
        [
            'asc',          # 'old files' 
            'desc'          # 'new files'
            'r_asc'         # 'olds by year'
            'r_desc'        # 'news by year'
            'title_asc'     # 'name up'
            'title_desc'    # 'name down'
            'views_asc', 
            'views_dasc', 
            'rating_asc', 
            'rating_dasc', 
            'stars_asc', 
            'stars_dasc'
        ],
        'desc'
    ],
    'pageNumber': [range(1, 20), 1],
}

from ._urls import URLS
from ._fetch import get_items_data
from ._logger import logger

def getItems(**infos):
    toRemove = []
    for key, value in infos.items():
        # toRemove = []
        if key not in allokwargs.keys():
            toRemove.append(key)
        else:
            if value not in allokwargs[key][0]:
                infos[key] = allokwargs[key][1]

    for key in toRemove:
        infos.pop(key)

    for key, value in allokwargs.items():
        if key not in infos.keys():
            infos[key] = value[1]

    # Prepare the url
    url = URLS.ALL_ITEMS.format(infos['itemsPerPage'], infos['level'], infos['videoKind'], infos['sortParam'], infos['pageNumber'])

    # Get the data
    logger.debug('get data from : {}'.format(url))
    data, info = get_items_data(url)

    if data:
        return data[0], info
    
    else:
        # delete the last entry cache, so it won't return null next time
        get_items_data.delete(url)
        return data, info

