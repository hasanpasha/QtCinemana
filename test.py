
from cinemanaAPI import *


search_k = str(input('Enter search name: '))

search_result, _ = search(videoTitle=search_k, type=['movie', 'series'])

kind = lambda a: 'movie' if a == '1' else 'series'

# print(search_result)
for i in search_result:
    print(f"{i['ar_title']} {kind(i['kind'])}")