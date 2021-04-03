
# filename: _fetch.py
# date: 2021/4/3 Sat

from ._options import Options 

from ring import lru
from json import loads
from requests import get

from ._logger import logger

def get_data(url):
    """ fetch the data """
    try:
        logger.debug('fetching data')
        resp = get(url, timeout=Options.TIMEOUT)

    # Handle errors 
    except Exception as e:
        logger.error(e)
        return False, e

    else:
        return resp, True
        

def get_json_data(resp):
    try:
        logger.debug('getting json data')
        data = loads(resp.text)
    
    except Exception as e:
        logger.error(e)
        raise e

    else:
        if data:
            logger.info('data fetched successfully')
            return data, "DATA AVAILABLE"          # Return json data
        else:
            logger.error('No data available this far')
            return data, "NO DATA"


@lru(maxsize=Options.SEARCH_CACHE_MAXSIZE, expire=Options.SEARCH_CACHE_EXPIRE)
def get_search_data(url):
    resp, info = get_data(url)
    if resp:
        return get_json_data(resp)

    else:
        return False, info


@lru(maxsize=Options.VIDEOS_CACHE_MAXSIZE, expire=Options.VIDEOS_CACHE_EXPIRE)
def get_videos_data(url):
    resp, info = get_data(url)
    if resp:
        return get_json_data(resp)

    else:
        return False, info


@lru(maxsize=Options.EPISODES_CACHE_MAXSIZE, expire=Options.EPISODES_CACHE_EXPIRE)
def get_episodes_data(url):
    resp, info = get_data(url)
    if resp:
        return get_json_data(resp)

    else:
        return False, info

@lru(maxsize=Options.INFOS_CACHE_MAXSIZE, expire=Options.INFOS_CACHE_EXPIRE)
def get_info_data(url):
    resp, info = get_data(url)
    if resp:
        return get_json_data(resp)

    else:
        return False, info

@lru(maxsize=Options.ITEMS_CACHE_MAXSIZE, expire=Options.ITEMS_CACHE_EXPIRE)
def get_items_data(url):
    resp, info = get_data(url)
    if resp:
        return get_json_data(resp)

    else:
        return False, info